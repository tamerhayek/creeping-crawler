"""ESPN-specific content parser (espn.com).

TODO — before this parser is production-ready, inspect a few ESPN article pages
and fill in the two constants below:
  - ARTICLE_SELECTOR: CSS selector for the main article container.
  - NOISE_SELECTORS:  CSS selectors for elements to strip before extraction
                      (ads, scoreboards, related stories, video players, etc.).
"""

from bs4 import BeautifulSoup, Tag

from .base import ContentParser


class EspnParser(ContentParser):
    """Parser for ESPN articles and sports content.

    Pipeline:
      1. Strip known noise elements from the DOM.
      2. Select the article container with ARTICLE_SELECTOR.
      3. Walk heading and paragraph elements, collecting text.
    """

    # TODO: set to the CSS selector that wraps the article body.
    # Inspect an ESPN article and look for the container of the article text
    # (e.g. ".article-body", "[data-testid='prism-article-body']").
    ARTICLE_SELECTOR: str = ""

    # TODO: list CSS selectors for elements to remove before extraction
    # (scoreboards, ad units, video embeds, related stories, etc.).
    # Example: [".InlineStory", ".Ad__content", ".VideoContainer"]
    NOISE_SELECTORS: list[str] = []

    _HEADING_TAGS = {"h1", "h2", "h3", "h4"}
    _CONTENT_TAGS = {"p"}

    def parse(self, url: str, html: str) -> str:
        """Extract clean article text from raw ESPN HTML.

        Args:
            url:  source URL (unused, kept for interface compatibility).
            html: raw HTML string from Crawl4AI.

        Returns:
            Plain text with paragraphs separated by blank lines.
            Empty string if nothing could be extracted.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove noise elements before any extraction
        for selector in self.NOISE_SELECTORS:
            for el in soup.select(selector):
                el.decompose()

        # TODO: replace fallback (soup.body) with the correct ARTICLE_SELECTOR
        body = (
            soup.select_one(self.ARTICLE_SELECTOR)
            if self.ARTICLE_SELECTOR
            else soup.body
        ) or soup

        collected: list[str] = []

        for element in body.find_all(self._HEADING_TAGS | self._CONTENT_TAGS):
            if not isinstance(element, Tag):
                continue
            text = element.get_text(separator=" ", strip=True)
            if text:
                collected.append(text)

        return "\n\n".join(collected)
