"""CNBC-specific content parser (www.cnbc.com).

Receives Crawl4AI markdown (filtered by CrawlerRunConfig) and removes
boilerplate sections that may still appear after the article body.
"""

from .base import ContentParser


class CnbcParser(ContentParser):
    """Parser for CNBC news articles.

    CrawlerRunConfig handles nav/footer/ad/newsletter removal.
    This parser stops at known boilerplate section headings.
    """

    EXCLUDED_SECTIONS = frozenset({
        "related content", "more from cnbc", "trending now",
        "you may also like", "watch now", "sign up",
    })

    def parse(self, url: str, markdown: str) -> str:
        """Return cleaned Crawl4AI markdown for CNBC pages."""
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
