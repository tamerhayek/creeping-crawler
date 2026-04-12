import re

from .base import ContentParser


class WikipediaParser(ContentParser):
    EXCLUDED_SECTIONS = {
        "see also",
        "references",
        "notes",
        "citations",
        "further reading",
        "external links",
        "sources",
        "bibliography",
        "works cited",
        "footnotes",
        "notes and references",
        "references and notes",
        "collegamenti esterni",
        "note",
        "riferimenti",
        "bibliografia",
        "fonti",
        "altri progetti",
        "voci correlate",
    }

    def parse(self, url: str, markdown: str) -> str:
        lines = markdown.splitlines()
        collected_lines: list[str] = []
        skip_section = False

        for raw_line in lines:
            line = raw_line.rstrip()

            if self._is_heading(line):
                heading = self._normalize_heading(line)
                skip_section = heading in self.EXCLUDED_SECTIONS
                if not skip_section and heading:
                    collected_lines.append(self._render_heading(line))
                continue

            if skip_section:
                continue

            if self._should_skip_line(line):
                continue

            collected_lines.append(line)

        return self._clean_output(collected_lines)

    def _is_heading(self, line: str) -> bool:
        return line.lstrip().startswith("#")

    def _normalize_heading(self, line: str) -> str:
        heading = self._render_heading(line)
        return re.sub(r"\s+", " ", heading).strip().lower()

    def _render_heading(self, line: str) -> str:
        return line.lstrip("#").strip()

    def _should_skip_line(self, line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False

        if stripped.startswith(("![]", "[![")):
            return True

        if stripped.startswith(("Category:", "Categories:", "Categoria:", "Categorie:")):
            return True

        return False

    def _clean_output(self, lines: list[str]) -> str:
        text = "\n".join(lines)
        text = re.sub(r"\[\d+\]", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
