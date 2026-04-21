"""Wikipedia-specific content parser.

Uses BeautifulSoup to extract clean body text directly from the raw HTML
returned by Crawl4AI. Stops collecting when it encounters a non-informative
section (references, bibliography, external links, etc.).

No per-page configuration is required — the parser works generically
for any en.wikipedia.org or it.wikipedia.org article.
"""

from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from .base import ContentParser


class WikipediaParser(ContentParser):
    """Parser for Wikipedia articles (any language subdomain).

    Pipeline:
      1. Parse raw HTML with BeautifulSoup.
      2. Walk the article body element by element.
      3. For heading elements: normalise text, stop if it matches EXCLUDED_SECTIONS.
      4. For paragraph/list elements: extract text and collect it.
    """

    # Headings that signal the end of informative content.
    EXCLUDED_SECTIONS = frozenset(
        {
            # English
            "see also", "references", "notes", "citations",
            "further reading", "external links", "sources",
            "bibliography", "works cited", "footnotes",
            "notes and references", "references and notes",
            # Italian
            "collegamenti esterni", "note", "riferimenti",
            "bibliografia", "fonti", "altri progetti", "voci correlate",
        }
    )

    _HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
    _CONTENT_TAGS = {"p", "li"}

    def parse(self, url: str, html: str) -> str:
        """Extract clean article text from raw Wikipedia HTML.

        Args:
            url:  source URL (unused, kept for interface compatibility).
            html: raw HTML string from Crawl4AI.

        Returns:
            Plain text with one paragraph/item per line, sections separated
            by blank lines. Empty string if nothing could be extracted.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Wikipedia article body lives in .mw-parser-output
        body = soup.select_one(".mw-parser-output") or soup.body or soup
        if body is None:
            return ""

        collected: list[str] = []

        for element in body.find_all(self._HEADING_TAGS | self._CONTENT_TAGS):
            if not isinstance(element, Tag):
                continue

            if element.name in self._HEADING_TAGS:
                heading = self._extract_heading_text(element)
                if not heading:
                    continue
                if heading in self.EXCLUDED_SECTIONS:
                    break  # stop — everything after this is non-informative
                collected.append(heading)

            else:
                text = element.get_text(separator=" ", strip=True)
                if text:
                    collected.append(text)

        return "\n\n".join(collected)

    def _extract_heading_text(self, element: Tag) -> str:
        """Return the normalised, lowercase heading text with edit links removed."""
        # Remove [edit] / [modifica] spans that Wikipedia injects
        for edit_span in element.find_all("span", class_="mw-editsection"):
            edit_span.decompose()

        return element.get_text(separator=" ", strip=True).lower()
