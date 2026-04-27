"""ESPN-specific content parser (www.espn.com).

Receives Crawl4AI markdown (filtered by CrawlerRunConfig) and removes
boilerplate sections and residual lines that may still appear after
the article body.
"""

import re

from ..base import ContentParser


class EspnParser(ContentParser):
    """Parser for ESPN articles.

    CrawlerRunConfig handles nav/footer/sidebar/ad removal.
    This parser stops at known boilerplate section headings and strips
    residual boilerplate lines that can leak through markdown conversion.
    """

    # Heading-level section names that signal end of editorial content.
    EXCLUDED_SECTIONS = frozenset({
        "advertisement",
        "trending",
        "top stories",
        "more from espn",
        "related content",
        "you may also like",
        "related stories",
        "editors' picks",
    })

    # Regex patterns for non-editorial lines to drop outright.
    _SKIP_PATTERNS: tuple[re.Pattern, ...] = (
        # "WATCH:" or "READ:" inline promos
        re.compile(r"^\**\s*(WATCH|READ)\s*:\**", re.IGNORECASE),
        # Lines that are only a markdown link (related articles, topic tags)
        re.compile(r"^\s*\[[^\]]+\]\([^)]+\)\s*$"),
        # List-item lines whose only content is a link, optionally wrapped in
        # bold markers (**).  ESPN injects related-article promo blocks in the
        # form:  **-[Title](url)  /  - [Title](url)**  /  **-[Title](url)**
        re.compile(r"^\s*\**-\s*(?:[^\[\n]*:\s*)?\[[^\]]+\]\([^)]+\)\**\s*$"),
        # Social / follow lines
        re.compile(r"follow us on", re.IGNORECASE),
        # Photo caption prefix (caption appears as standalone italic line)
        re.compile(r"^\s*\*[^*]+\*\s*$"),
    )

    def parse(self, url: str, markdown: str) -> str:
        """Return cleaned Crawl4AI markdown for ESPN pages."""
        collected: list[str] = []

        for line in markdown.split("\n"):
            # Stop at known boilerplate headings.
            if line.startswith("#"):
                heading = line.lstrip("#").strip().lower()
                if any(heading == s or heading.startswith(s) for s in self.EXCLUDED_SECTIONS):
                    break

            # Drop residual boilerplate lines.
            if any(pat.search(line) for pat in self._SKIP_PATTERNS):
                continue

            collected.append(line)

        # Strip trailing blank lines.
        while collected and not collected[-1].strip():
            collected.pop()

        return "\n".join(collected)
