"""CNBC-specific content parser (www.cnbc.com).

Receives Crawl4AI markdown (filtered by CrawlerRunConfig) and removes
boilerplate sections that may still appear after the article body.
"""

import re

from ..base import ContentParser


class CnbcParser(ContentParser):
    """Parser for CNBC news articles.

    CrawlerRunConfig handles nav/footer/ad/newsletter removal.
    This parser stops at known boilerplate section headings and strips
    residual boilerplate lines that can leak through markdown conversion.
    """

    # Heading-level section names that signal end of editorial content.
    EXCLUDED_SECTIONS = frozenset({
        "related content",
        "more from cnbc",
        "trending now",
        "you may also like",
        "watch now",
        "sign up",
        "watch live",
        "more in",
        "sponsored content",
        "advertisement",
    })

    # Regex patterns for non-editorial lines to drop outright.
    _SKIP_PATTERNS: tuple[re.Pattern, ...] = (
        # "Choose CNBC as your preferred source on Google News"
        re.compile(r"choose cnbc", re.IGNORECASE),
        # "Follow us on" social media lines
        re.compile(r"follow us on", re.IGNORECASE),
        # "Subscribe to CNBC" newsletter / app CTAs
        re.compile(r"subscribe to cnbc", re.IGNORECASE),
        # Standalone bracketed image labels  e.g. "[Photo: ...]"  or "[VIDEO]"
        re.compile(r"^\[(?:photo|video|image|watch)[^\]]*\]\s*$", re.IGNORECASE),
        # Lines that are only a markdown link with no surrounding text
        re.compile(r"^\s*\[[^\]]+\]\([^)]+\)\s*$"),
        # "Read more:" or "Read also:" intra-article promos
        re.compile(r"^read (more|also)\s*:", re.IGNORECASE),
        # "WATCH: [link]" inline video promos (bold or plain)
        re.compile(r"^\**\s*WATCH\s*:\**", re.IGNORECASE),
    )

    def parse(self, url: str, markdown: str) -> str:
        """Return cleaned Crawl4AI markdown for CNBC pages."""
        collected: list[str] = []

        for line in markdown.split("\n"):
            # Stop at known boilerplate headings.
            if line.startswith("#"):
                heading = line.lstrip("#").strip().lower()
                if any(heading == s or heading.startswith(s) for s in self.EXCLUDED_SECTIONS):
                    break

                # Remove bold/italic markers wrapping only whitespace (e.g. "** **")
            line = re.sub(r'\*{1,3}\s*\*{1,3}', '', line)

            # Drop residual boilerplate lines.
            if any(pat.search(line) for pat in self._SKIP_PATTERNS):
                continue

            collected.append(line)

        # Strip trailing blank lines.
        while collected and not collected[-1].strip():
            collected.pop()

        return "\n".join(collected)
