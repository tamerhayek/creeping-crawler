"""XE-specific content parser (www.xe.com).

Receives Crawl4AI markdown (filtered by CrawlerRunConfig) and returns it
cleaned of any trailing boilerplate sections.
"""

from .base import ContentParser


class XeParser(ContentParser):
    """Parser for XE currency pages.

    CrawlerRunConfig handles table/nav/footer/cta/banner removal.
    This parser stops at known boilerplate section headings.
    """

    EXCLUDED_SECTIONS = frozenset({
        "related articles", "related posts", "you may also like",
        "sign up", "get started", "popular currencies",
    })

    def parse(self, url: str, markdown: str) -> str:
        """Return cleaned Crawl4AI markdown for XE pages."""
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
