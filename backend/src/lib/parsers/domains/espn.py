"""ESPN-specific content parser (www.espn.com).

Receives Crawl4AI markdown (filtered by CrawlerRunConfig) and removes
boilerplate sections and residual lines that may still appear after
the article body.
"""

import re

from ..base import ContentParser


class EspnParser(ContentParser):
    """Parser for ESPN pages.

    CrawlerRunConfig handles nav/footer/sidebar/ad removal.
    This parser stops at known boilerplate section headings and strips
    residual boilerplate lines that can leak through markdown conversion.

    For player stats pages (/player/stats/) content is collected starting
    from the "Stats" heading; all other pages collect from the top.
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

    # Footer/legal lines that signal end of useful content on any page.
    # Patterns intentionally avoid ^ and $ anchors so they match even when
    # the text is embedded in a markdown list item (- Terms of Use) or link
    # ([Terms of Use](...)).
    _FOOTER_PATTERNS: tuple[re.Pattern, ...] = (
        re.compile(r"terms of use", re.IGNORECASE),
        re.compile(r"privacy policy", re.IGNORECASE),
        re.compile(r"cookie policy", re.IGNORECASE),
        re.compile(r"interest.based ads", re.IGNORECASE),
        re.compile(r"eu privacy rights", re.IGNORECASE),
        re.compile(r"manage privacy preferences", re.IGNORECASE),
        re.compile(r"espn enterprises", re.IGNORECASE),
        re.compile(r"all rights reserved", re.IGNORECASE),
    )

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
        # Web font observer test string injected by ESPN's font loader
        re.compile(r"^BESbswy", re.IGNORECASE),
    )

    # Regex to detect the start of the stats section on player stats pages.
    _STATS_HEADING = re.compile(r"^#+\s*Stats\s*$|^Stats\s*$", re.IGNORECASE)

    def parse(self, url: str, markdown: str) -> str:
        """Return cleaned Crawl4AI markdown for ESPN pages."""
        stats_page = "/player/stats/" in url
        collected: list[str] = []
        in_content = not stats_page  # stats pages: wait for the Stats heading

        for line in markdown.split("\n"):
            if not in_content:
                if self._STATS_HEADING.match(line):
                    in_content = True
                    collected.append("Stats")
                continue

            # Stop at footer/legal lines.
            if any(pat.search(line) for pat in self._FOOTER_PATTERNS):
                break

            # Stop at known boilerplate headings.
            if line.startswith("#"):
                heading = line.lstrip("#").strip().lower()
                if any(heading == s or heading.startswith(s) for s in self.EXCLUDED_SECTIONS):
                    break

            # Drop residual boilerplate lines.
            if any(pat.search(line) for pat in self._SKIP_PATTERNS):
                continue

            collected.append(line)

        while collected and not collected[-1].strip():
            collected.pop()

        return "\n".join(collected)
