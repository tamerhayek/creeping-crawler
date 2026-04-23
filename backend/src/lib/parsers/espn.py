"""ESPN-specific content parser (www.espn.com).

Receives Crawl4AI markdown (filtered by CrawlerRunConfig) and removes
boilerplate sections that may still appear after the article body.
"""

from .base import ContentParser


class EspnParser(ContentParser):
    """Parser for ESPN articles.

    CrawlerRunConfig handles nav/footer/ad/sidebar removal.
    This parser stops at known boilerplate section headings.
    """

    EXCLUDED_SECTIONS = frozenset({
        "advertisement", "trending", "top stories",
        "more from espn", "related content", "you may also like",
    })

    def parse(self, url: str, markdown: str) -> str:
        """Return cleaned Crawl4AI markdown for ESPN pages."""
        collected: list[str] = []

        for line in markdown.split("\n"):
            if line.startswith("#"):
                heading = line.lstrip("#").strip().lower()
                if heading in self.EXCLUDED_SECTIONS:
                    break
            collected.append(line)

        while collected and not collected[-1].strip():
            collected.pop()

        return "\n".join(collected)
