"""Wikipedia-specific content parser.

Receives Crawl4AI markdown (already filtered by CrawlerRunConfig) and
removes non-informative trailing sections plus residual boilerplate lines.
"""

from __future__ import annotations

import re

from ..base import ContentParser


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
        # Skip-navigation links: "[Vai al contenuto](...)", "[Salta a](...)"
        re.compile(r"^\[vai al\b", re.IGNORECASE),
        re.compile(r"^\[salta al?\b", re.IGNORECASE),
        # Lines that are only wiki-style image/file markup residues
        re.compile(r"^\s*!\["),
    )

    # Footnote reference markers to strip inline: [1], [4], [12], [N 1], [N 2], etc.
    # Limited to 1-3 digit numbers to avoid stripping year links like [1912].
    _FOOTNOTE_RE = re.compile(r"\[(?:\d{1,3}|N\s*\d+)\]")

    # Protocol-relative markdown links that Crawl4AI emits for internal Wikipedia
    # links: [testo](//it.wikipedia.org/wiki/X "X") → keep only link text.
    # \S* handles URLs with parentheses e.g. /wiki/Ontologia_(informatica).
    _PROTO_REL_LINK_RE = re.compile(r'\[([^\]]*)\]\(//\S*(?:\s+"[^"]*")?\)')

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

            line = self._PROTO_REL_LINK_RE.sub(r"\1", line)
            line = self._FOOTNOTE_RE.sub("", line)

            # Drop image residue that substitutions may have exposed.
            if re.match(r"^\s*!\[", line):
                continue

            collected.append(line)

        while collected and not collected[-1].strip():
            collected.pop()

        return "\n".join(collected)
