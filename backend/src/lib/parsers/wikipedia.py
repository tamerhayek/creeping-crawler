"""Wikipedia-specific content parser.

Receives Crawl4AI markdown (already scoped to .mw-parser-output by css_selector)
and removes non-informative trailing sections.
"""

from __future__ import annotations

from .base import ContentParser


class WikipediaParser(ContentParser):
    """Parser for Wikipedia articles (any language subdomain).

    Pipeline:
      1. Walk the Crawl4AI markdown line by line.
      2. When a heading matches an excluded section, stop collecting.
      3. Return the cleaned markdown.
    """

    EXCLUDED_SECTIONS = frozenset({
        # English
        "see also", "references", "notes", "citations",
        "further reading", "external links", "sources",
        "bibliography", "works cited", "footnotes",
        "notes and references", "references and notes",
        # Italian
        "collegamenti esterni", "note", "riferimenti",
        "bibliografia", "fonti", "altri progetti", "voci correlate",
    })

    def parse(self, url: str, markdown: str) -> str:
        """Remove non-informative sections from Crawl4AI markdown.

        Args:
            url:      source URL (unused).
            markdown: raw markdown produced by Crawl4AI.

        Returns:
            Cleaned markdown stopping before the first excluded section heading.
        """
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
