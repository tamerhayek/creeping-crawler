"""XE-specific content parser (www.xe.com).

Receives Crawl4AI markdown (filtered by CrawlerRunConfig) and returns it
cleaned of trailing boilerplate sections, CTA links and pipe-table noise.
"""

import re

from ..base import ContentParser


class XeParser(ContentParser):
    """Parser for XE pages (blog articles + currency converter).

    On top of CrawlerRunConfig stripping (header, nav, footer, banners,
    Trustpilot block, CTA buttons), this parser:

      * stops at known boilerplate section headings,
      * stops at known plain-text boilerplate sentinels (sections that
        appear on the converter page without a markdown heading),
      * drops residual CTA links the gold standard never includes,
      * drops markdown horizontal rules,
      * linearises markdown tables (one cell per line, separator rows
        dropped) so table content contributes plain tokens to the
        evaluation set.
    """

    EXCLUDED_SECTIONS = frozenset({
        "related articles", "related posts", "you may also like",
        "sign up", "get started", "popular currencies",
        "xe is trusted by millions around the globe",
        "send money destinations",
    })

    # Plain-text (non-`#`) sentinel lines that mark the start of a
    # boilerplate block. Everything from the sentinel onwards is dropped.
    # Used for the converter page where these blocks are rendered as bare
    # text rather than markdown headings.
    _TERMINAL_LINES = frozenset({
        "send money destinations",
        "xe is trusted by millions around the globe",
        "trusted by",
    })

    # Plain-text lines that should be dropped individually (CTA / promo
    # snippets that the gold standard never includes).
    _DROP_LINES = frozenset({
        "did you know you can send money abroad with xe?",
        "add currency",
        "learn more",
    })

    # Links the gold standard strips out (CTA / download buttons that
    # survive the crawler config).
    _SKIP_LINK_PATTERNS = (
        re.compile(r'\[\s*Speak to an FX specialist', re.IGNORECASE),
        re.compile(r'\[\s*Download the Global Currency Outlook', re.IGNORECASE),
        # "[Learn more](/send-money/)" CTA links on each tool tile of the
        # converter page.
        re.compile(r'^\s*\[\s*Learn more\s*\]\(', re.IGNORECASE),
    )

    # Markdown table separator row, e.g. "| --- | --- |".
    _TABLE_SEP_RE = re.compile(r'^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?$')

    # Markdown horizontal rule, e.g. "* * *" or "---".
    _HR_RE = re.compile(r'^(\*\s*){3,}$|^-{3,}$|^_{3,}$')

    # Crawl4AI sometimes emits "**word** ," (space between closing bold
    # and trailing punctuation). After markdown stripping that becomes
    # "word ," which tokenises as "word" + ",", whereas the gold standard
    # has the punctuation glued to the previous word ("word,").
    _BOLD_PUNCT_RE = re.compile(r'\*\* +([,.;:!?\)])')

    @staticmethod
    def _table_row_cells(line: str) -> list[str]:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        return [c for c in cells if c]

    def parse(self, url: str, markdown: str) -> str:
        markdown = self._BOLD_PUNCT_RE.sub(r'**\1', markdown)
        out: list[str] = []

        for raw in markdown.split("\n"):
            line = raw.rstrip()
            stripped = line.strip()
            lowered = stripped.lower()

            if line.startswith("#"):
                heading = line.lstrip("#").strip().lower()
                if heading in self.EXCLUDED_SECTIONS:
                    break

            if lowered in self._TERMINAL_LINES:
                break

            if lowered in self._DROP_LINES:
                continue

            if self._HR_RE.match(stripped):
                continue

            if self._TABLE_SEP_RE.match(stripped):
                continue

            if any(p.search(stripped) for p in self._SKIP_LINK_PATTERNS):
                continue

            # Pipe-formatted table data row: split into one cell per line.
            if stripped.startswith("|") and "|" in stripped[1:]:
                out.extend(self._table_row_cells(stripped))
                continue

            out.append(line)

        while out and not out[-1].strip():
            out.pop()

        return "\n".join(out)
