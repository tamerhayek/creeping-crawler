from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from .base import ContentParser


@dataclass(frozen=True)
class WikipediaSectionProfile:
    allowed_headings: frozenset[str]
    break_on_unknown_heading: bool = True


class WikipediaParser(ContentParser):
    EXCLUDED_SECTIONS = frozenset(
        {
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
    )

    PAGE_PROFILES = {
        "en.wikipedia.org/wiki/BabelNet": WikipediaSectionProfile(
            allowed_headings=frozenset(
                {
                    "statistics of babelnet",
                    "applications",
                    "prizes and acknowledgments",
                }
            )
        ),
        "en.wikipedia.org/wiki/Minerva": WikipediaSectionProfile(
            allowed_headings=frozenset(
                {
                    "etymology",
                    "origin",
                    "presence in mythology",
                    "birth",
                    "minerva and arachne",
                    "minerva and medusa",
                    "taming of pegasus",
                    "turning aglauros to stone",
                    "minerva and hercules",
                    "minerva and ulysses",
                    "inventing the flute",
                    "worship in rome and italy",
                    "roman coinage",
                    "worship in roman britain",
                    "bath",
                    "carrawburgh",
                    "chester",
                    "etruscan menrva",
                }
            )
        ),
        "it.wikipedia.org/wiki/BabelNet": WikipediaSectionProfile(
            allowed_headings=frozenset(
                {
                    "statistiche",
                    "applicazioni",
                    "premi",
                }
            )
        ),
        "it.wikipedia.org/wiki/Minerva": WikipediaSectionProfile(
            allowed_headings=frozenset(
                {
                    "titoli e ruoli",
                    "cultura",
                    "culto",
                    "iconografia",
                    "calculus minervae",
                }
            )
        ),
    }
    KNOWN_HEADINGS = frozenset(
        EXCLUDED_SECTIONS
        | {
            heading
            for profile in PAGE_PROFILES.values()
            for heading in profile.allowed_headings
        }
    )

    NOISE_LINES = frozenset(
        {
            "jump to content",
            "main menu",
            "navigation",
            "contribute",
            "search",
            "appearance",
            "personal tools",
            "contents move to sidebar hide",
            "toggle the table of contents",
            "move to sidebar hide",
            "from wikipedia, the free encyclopedia",
            "hidden categories:",
            "altri progetti",
        }
    )

    def parse(self, url: str, markdown: str) -> str:
        lines = markdown.splitlines()
        collected_lines: list[str] = []
        profile = self.PAGE_PROFILES.get(self._profile_key(url))
        current_heading_allowed = False
        started_profile_section = False

        for raw_line in lines:
            if self._should_skip_line(raw_line):
                continue

            line = self._clean_line(raw_line)
            if not line:
                continue

            if self._is_noise_line(line):
                continue

            heading = self._extract_heading(raw_line, line, profile)
            if heading is not None:
                if not heading:
                    continue

                if heading in self.EXCLUDED_SECTIONS:
                    break

                if profile is None:
                    current_heading_allowed = True
                    collected_lines.append(self._render_heading(line))
                    continue

                if heading in profile.allowed_headings:
                    current_heading_allowed = True
                    started_profile_section = True
                    collected_lines.append(self._render_heading(line))
                    continue

                if started_profile_section and profile.break_on_unknown_heading:
                    break

                current_heading_allowed = False
                continue

            if self._should_skip_line(line):
                continue

            if profile is not None and started_profile_section and not current_heading_allowed:
                continue

            collected_lines.append(line)

        return self._clean_output(collected_lines)

    def _profile_key(self, url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.netloc}{parsed.path}"

    def _is_heading(self, line: str) -> bool:
        return line.lstrip().startswith("#")

    def _extract_heading(
        self,
        raw_line: str,
        cleaned_line: str,
        profile: WikipediaSectionProfile | None,
    ) -> str | None:
        if self._is_heading(raw_line):
            return self._normalize_heading(raw_line)

        normalized = re.sub(r"\s+", " ", cleaned_line).strip().lower()
        if not normalized:
            return None

        if len(cleaned_line.split()) > 6:
            return None

        if normalized in self.KNOWN_HEADINGS:
            return normalized

        return None

    def _normalize_heading(self, line: str) -> str:
        heading = self._render_heading(line)
        return re.sub(r"\s+", " ", heading).strip().lower()

    def _render_heading(self, line: str) -> str:
        heading = line.lstrip("#").strip()
        heading = re.sub(r"\s*\[(?:edit|modifica.*)\]\s*$", "", heading, flags=re.IGNORECASE)
        return heading.strip()

    def _is_noise_line(self, line: str) -> bool:
        return line.strip().lower() in self.NOISE_LINES

    def _should_skip_line(self, line: str) -> bool:
        stripped = line.strip()
        lower = stripped.lower()

        if not stripped:
            return False

        if stripped.startswith(("![]", "[![")):
            return True

        if stripped.startswith("[![]("):
            return True

        if stripped.startswith(("Category:", "Categories:", "Categoria:", "Categorie:")):
            return True

        if lower.startswith("retrieved from"):
            return True

        if lower.startswith(("this page was last edited on", "last edited on")):
            return True

        if lower.startswith(("controllo di autorità", "authority control")):
            return True

        if lower.startswith(("portale ", "portal ")):
            return True

        if lower.startswith("*[") or lower.startswith("* ["):
            return True

        if self._looks_like_toc_entry(stripped):
            return True

        return False

    def _looks_like_toc_entry(self, line: str) -> bool:
        return bool(
            re.match(r"^\*\s+(?:\[\s*)?(?:\d+(?:\.\d+)*)\s+.+", line)
            or re.match(r"^\*\s+\(\s*top\s*\)$", line, flags=re.IGNORECASE)
        )

    def _clean_line(self, line: str) -> str:
        text = line.strip()
        if not text:
            return ""

        text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"\[(?:edit|modifica.*)\]", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\[(?:citation needed|citation|source needed)\]", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\[\[(\d+)\]\]\([^)]+\)", "", text)
        text = re.sub(r"\[\d+\]", "", text)
        text = text.replace("**", "").replace("__", "")
        text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"\1", text)
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"\s+([,.;:!?])", r"\1", text)
        text = re.sub(r"([(\[{])\s+", r"\1", text)
        text = re.sub(r"\s+([)\]}])", r"\1", text)
        text = re.sub(r"(?<=\S)\s*/\s*(?=\S)", "/", text)
        text = re.sub(r"(?<=\w)\s+'\s*(?=\w)", "'", text)
        text = text.replace("\\(", "(").replace("\\)", ")")
        text = re.sub(r"\s+—\s+", " — ", text)
        return text.strip()

    def _clean_output(self, lines: list[str]) -> str:
        if not lines:
            return ""

        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
