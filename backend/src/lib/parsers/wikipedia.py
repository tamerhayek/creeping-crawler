"""Wikipedia-specific content parser.

Filters raw Crawl4AI markdown to keep only the informative body text,
dropping navigation noise, boilerplate, and unwanted sections.

Page profiles (WikipediaSectionProfile) allow per-page control over
which sections to include. Pages without a profile get all sections
except those in EXCLUDED_SECTIONS.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from .base import ContentParser

@dataclass(frozen=True)
class WikipediaSectionProfile:
    """Per-page section filter for WikipediaParser.

    Attributes:
        allowed_headings:         lowercase heading names to include.
        break_on_unknown_heading: if True, stop collecting as soon as an
                                  unrecognised heading is encountered.
    """

    allowed_headings: frozenset[str]
    break_on_unknown_heading: bool = True

class WikipediaParser(ContentParser):
    """Parser for en.wikipedia.org and it.wikipedia.org pages.

    Pipeline per line:
      1. Skip lines that should never appear (images, ToC entries, categories…).
      2. Clean inline markdown and punctuation artefacts.
      3. Detect headings (both markdown # syntax and plain known-heading text).
      4. Apply section filtering: skip or collect lines based on the active heading.
      5. Join collected lines and normalise whitespace.
    """

    # Sections that terminate collection for all pages.
    EXCLUDED_SECTIONS = frozenset(
        {
            "see also", "references", "notes", "citations",
            "further reading", "external links", "sources",
            "bibliography", "works cited", "footnotes",
            "notes and references", "references and notes",
            # Italian equivalents
            "collegamenti esterni", "note", "riferimenti",
            "bibliografia", "fonti", "altri progetti", "voci correlate",
        }
    )

    # Per-page profiles: keys are "{netloc}{path}" strings.
    PAGE_PROFILES: dict[str, WikipediaSectionProfile] = {
        "en.wikipedia.org/wiki/BabelNet": WikipediaSectionProfile(
            allowed_headings=frozenset(
                {"statistics of babelnet", "applications", "prizes and acknowledgments"}
            )
        ),
        "en.wikipedia.org/wiki/Minerva": WikipediaSectionProfile(
            allowed_headings=frozenset(
                {
                    "etymology", "origin", "presence in mythology", "birth",
                    "minerva and arachne", "minerva and medusa", "taming of pegasus",
                    "turning aglauros to stone", "minerva and hercules",
                    "minerva and ulysses", "inventing the flute",
                    "worship in rome and italy", "roman coinage",
                    "worship in roman britain", "bath", "carrawburgh", "chester",
                    "etruscan menrva",
                }
            )
        ),
        "it.wikipedia.org/wiki/BabelNet": WikipediaSectionProfile(
            allowed_headings=frozenset({"statistiche", "applicazioni", "premi"})
        ),
        "it.wikipedia.org/wiki/Minerva": WikipediaSectionProfile(
            allowed_headings=frozenset(
                {"titoli e ruoli", "cultura", "culto", "iconografia", "calculus minervae"}
            )
        ),
    }

    # Union of all headings across all profiles and the exclusion list.
    # Used to detect plain-text headings not formatted with #.
    KNOWN_HEADINGS = frozenset(
        EXCLUDED_SECTIONS
        | {h for profile in PAGE_PROFILES.values() for h in profile.allowed_headings}
    )

    # Lines that are always noise regardless of section context.
    NOISE_LINES = frozenset(
        {
            "jump to content", "main menu", "navigation", "contribute",
            "search", "appearance", "personal tools",
            "contents move to sidebar hide", "toggle the table of contents",
            "move to sidebar hide", "from wikipedia, the free encyclopedia",
            "hidden categories:", "altri progetti",
        }
    )

    # ------------------------------------------------------------------ #
    # Public interface                                                     #
    # ------------------------------------------------------------------ #

    def parse(self, url: str, markdown: str) -> str:
        """Parse Wikipedia markdown and return filtered body text."""
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
                    break  # stop at bibliography / references / etc.

                if profile is None:
                    # No profile: include all non-excluded sections.
                    current_heading_allowed = True
                    collected_lines.append(self._render_heading(line))
                    continue

                if heading in profile.allowed_headings:
                    current_heading_allowed = True
                    started_profile_section = True
                    collected_lines.append(self._render_heading(line))
                    continue

                if started_profile_section and profile.break_on_unknown_heading:
                    break  # unknown heading after an allowed one → stop

                current_heading_allowed = False
                continue

            if self._should_skip_line(line):
                continue

            if profile is not None and started_profile_section and not current_heading_allowed:
                continue

            collected_lines.append(line)

        return self._clean_output(collected_lines)

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _profile_key(self, url: str) -> str:
        """Return the profile lookup key for the given URL (netloc + path)."""
        parsed = urlparse(url)
        return f"{parsed.netloc}{parsed.path}"

    def _is_heading(self, line: str) -> bool:
        """Return True if the line starts with a markdown heading marker (#)."""
        return line.lstrip().startswith("#")

    def _extract_heading(
        self,
        raw_line: str,
        cleaned_line: str,
        profile: WikipediaSectionProfile | None,
    ) -> str | None:
        """Detect whether a line is a heading and return its normalised text.

        Returns:
            - A non-empty string: the normalised heading name.
            - An empty string:    the line is a heading but should be skipped.
            - None:               the line is not a heading.
        """
        if self._is_heading(raw_line):
            return self._normalize_heading(raw_line)

        # Some Wikipedia pages render headings as plain text (no # markers).
        # Detect them by matching against KNOWN_HEADINGS if the line is short.
        normalized = re.sub(r"\s+", " ", cleaned_line).strip().lower()
        if not normalized:
            return None

        if len(cleaned_line.split()) > 6:
            return None  # too long to be a heading

        if normalized in self.KNOWN_HEADINGS:
            return normalized

        return None

    def _normalize_heading(self, line: str) -> str:
        """Strip # markers and [edit] links, then lowercase."""
        heading = self._render_heading(line)
        return re.sub(r"\s+", " ", heading).strip().lower()

    def _render_heading(self, line: str) -> str:
        """Remove # markers and [edit] / [modifica] suffixes from a heading."""
        heading = line.lstrip("#").strip()
        heading = re.sub(r"\s*\[(?:edit|modifica.*)\]\s*$", "", heading, flags=re.IGNORECASE)
        return heading.strip()

    def _is_noise_line(self, line: str) -> bool:
        """Return True if the line matches a known UI noise pattern."""
        return line.strip().lower() in self.NOISE_LINES

    def _should_skip_line(self, line: str) -> bool:
        """Return True if the line should be discarded before any other processing."""
        stripped = line.strip()
        lower = stripped.lower()

        if not stripped:
            return False  # blank lines are handled downstream

        if stripped.startswith(("![]", "[![")):
            return True  # standalone images

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
        """Return True if the line looks like an auto-generated ToC bullet."""
        return bool(
            re.match(r"^\*\s+(?:\[\s*)?(?:\d+(?:\.\d+)*)\s+.+", line)
            or re.match(r"^\*\s+\(\s*top\s*\)$", line, flags=re.IGNORECASE)
        )

    def _clean_line(self, line: str) -> str:
        """Remove inline markdown and normalise spacing on a single line."""
        text = line.strip()
        if not text:
            return ""

        text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)                         # images
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)                     # links → label
        text = re.sub(r"\[(?:edit|modifica.*)\]", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\[(?:citation needed|citation|source needed)\]", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\[\[(\d+)\]\]\([^)]+\)", "", text)                       # numeric refs
        text = re.sub(r"\[\d+\]", "", text)                                       # footnote refs
        text = text.replace("**", "").replace("__", "")
        text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"\1", text)                      # italic _..._
        text = re.sub(r"\s+", " ", text).strip()
        # Normalise punctuation spacing
        text = re.sub(r"\s+([,.;:!?])", r"\1", text)
        text = re.sub(r"([(\[{])\s+", r"\1", text)
        text = re.sub(r"\s+([)\]}])", r"\1", text)
        text = re.sub(r"(?<=\S)\s*/\s*(?=\S)", "/", text)
        text = re.sub(r"(?<=\w)\s+'\s*(?=\w)", "'", text)
        text = text.replace("\\(", "(").replace("\\)", ")")
        text = re.sub(r"\s+—\s+", " — ", text)
        return text.strip()

    def _clean_output(self, lines: list[str]) -> str:
        """Join collected lines and collapse excessive blank lines."""
        if not lines:
            return ""
        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
