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
        dropped)
    """

    # Headings that terminate the content (everything after is boilerplate).
    EXCLUDED_SECTIONS = frozenset({
        "related articles", "related posts", "you may also like",
        "sign up", "get started", "popular currencies",
        "xe is trusted by millions around the globe",
        "send money destinations",
        "international money transfers done right",
        
    })

    # Headings to drop in place without terminating the document.
    _DROP_SECTIONS = frozenset({
        "compare and save",
    })

    # Plain-text (non-`#`) lines that terminate the content.
    _TERMINAL_LINES = frozenset({
        "send money destinations",
        "xe is trusted by millions around the globe",
        "trusted by",
        "loading popular currency pairs...",
    })

    # Plain-text lines that should be dropped individually.
    _DROP_LINES = frozenset({
        "did you know you can send money abroad with xe?",
        "add currency",
    })

    # Standalone boilerplate paragraphs (matched on a line prefix)
    _DROP_PREFIXES = (
        "we use the mid-market rate",
        "when you compare xe to leading banks",
        "the comparison savings are based on",
    )

    # Links the gold standard strips out.
    _SKIP_LINK_PATTERNS = (
        re.compile(r'\[\s*Speak to an FX specialist', re.IGNORECASE),
        re.compile(r'\[\s*Download the Global Currency Outlook', re.IGNORECASE),
    )

    # Inline image: ``![alt](url)``.
    _IMAGE_RE = re.compile(r'!\[([^\]]*)\]\([^)]*\)')
    # Site logo image, dropped entirely
    _LOGO_RE = re.compile(r'!\[[^\]]*\]\([^)]*logo-xe[^)]*\)', re.IGNORECASE)
    # Inline link glued to preceding non-space text: ``rates[Send money](url)``.
    _GLUED_LINK_RE = re.compile(r'(\S)(\[[^\]]+\]\([^)]*\))')
    # Adjacent inline elements rendered without whitespace produce glued
    # camelCase tokens (``EuroEUR``, ``nationwideNationwide``); split them
    # back at the lowercase/uppercase boundary
    _CAMEL_RE = re.compile(r'(?<=[a-z])(?=[A-Z])')

    # Markdown table separator row, e.g. "| --- | --- |".
    _TABLE_SEP_RE = re.compile(r'^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?$')

    # Markdown horizontal rule, e.g. "* * *" or "---".
    _HR_RE = re.compile(r'^(\*\s*){3,}$|^-{3,}$|^_{3,}$')

    _BOLD_PUNCT_RE = re.compile(r'\*\* +([,.;:!?\)])')

    @staticmethod
    def _table_row_cells(line: str) -> list[str]:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        return [c for c in cells if c]

    def _preprocess(self, markdown: str) -> str:
        """Normalise images and glued links before line-level filtering."""
        markdown = self._BOLD_PUNCT_RE.sub(r'**\1', markdown)
        markdown = self._LOGO_RE.sub('', markdown)
        # Keep image alt text
        
        markdown = self._IMAGE_RE.sub(r'\1', markdown)
        # Break links that are glued onto preceding text onto their own line.
        markdown = self._GLUED_LINK_RE.sub(r'\1\n\2', markdown)
        # Separate glued camelCase tokens from adjacent inline elements.
        markdown = self._CAMEL_RE.sub(' ', markdown)
        return markdown

    def parse(self, url: str, markdown: str) -> str:
        markdown = self._preprocess(markdown)
        out: list[str] = []

        for raw in markdown.split("\n"):
            line = raw.rstrip()
            stripped = line.strip()
            lowered = stripped.lower()

            if line.startswith("#"):
                heading = line.lstrip("#").strip().lower()
                if heading in self.EXCLUDED_SECTIONS:
                    break
                if heading in self._DROP_SECTIONS:
                    continue

            if lowered in self._TERMINAL_LINES:
                break

            if lowered in self._DROP_LINES:
                continue

            if any(lowered.startswith(p) for p in self._DROP_PREFIXES):
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
