"""Wikipedia-specific content parser.

Receives Crawl4AI markdown (already filtered by CrawlerRunConfig) and
removes non-informative trailing sections plus residual boilerplate lines.
"""

from __future__ import annotations

import re

from .base import ContentParser


class WikipediaParser(ContentParser):
    """Parser for Wikipedia articles (any language subdomain).

    Pipeline:
      1. Walk the Crawl4AI markdown line by line.
      2. When a heading matches an excluded section, stop collecting.
      3. Drop residual boilerplate lines (edit links, coordinate lines, etc.).
      4. Return the cleaned markdown.
    """

    EXCLUDED_SECTIONS = frozenset({
        "collegamenti esterni", "note", "riferimenti",
        "bibliografia", "fonti", "altri progetti", "voci correlate",
    })

    _SKIP_PATTERNS: tuple[re.Pattern, ...] = (
        # Coordinate lines e.g. "43°N 12°E" or "Coordinate: 41°54′N 12°29′E"
        re.compile(r"coordinate[:\s]", re.IGNORECASE),
        re.compile(r"\d+[°][^\n]{0,30}[NSEW]"),
        # Bare edit-section links: "[modifica | modifica wikitesto]"
        re.compile(r"\[modifica", re.IGNORECASE),
        re.compile(r"\[edit\b", re.IGNORECASE),
        # Skip-navigation links: "[Vai al contenuto](...)", "[Salta a](...)"
        re.compile(r"^\[vai al\b", re.IGNORECASE),
        re.compile(r"^\[salta al?\b", re.IGNORECASE),
        # Disambiguation notice lines
        re.compile(r"^disambigua", re.IGNORECASE),
        # Lines that are only wiki-style image/file markup residues
        re.compile(r"^\s*!\["),
    )

    def parse(self, url: str, markdown: str) -> str:
        """Remove non-informative sections and boilerplate from Crawl4AI markdown."""
        collected: list[str] = []

        for line in markdown.split("\n"):
            if line.startswith("#"):
                heading = line.lstrip("#").strip().lower()
                if heading in self.EXCLUDED_SECTIONS:
                    break

            if any(pat.search(line) for pat in self._SKIP_PATTERNS):
                continue

            collected.append(line)

        while collected and not collected[-1].strip():
            collected.pop()

        return "\n".join(collected)
