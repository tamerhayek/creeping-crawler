from crawl_eval.parsers.wikipedia import WikipediaParser


def test_english_minerva_profile_keeps_only_selected_sections() -> None:
    parser = WikipediaParser()
    markdown = "\n".join(
        [
            "Minerva (/mɪˈnɜːrvə/) is the Roman goddess of wisdom.",
            "## Etymology",
            "Possible origin text.",
            "## Origin",
            "Origin text.",
            "## Presence in mythology",
            "Overview text.",
            "### Birth",
            "Birth text.",
            "### Minerva and Hercules",
            "Hercules text.",
            "### Minerva and Ulysses",
            "Ulysses text.",
            "## Worship in Rome and Italy",
            "Worship text.",
            "## References",
            "Should be dropped.",
        ]
    )

    parsed = parser.parse("https://en.wikipedia.org/wiki/Minerva", markdown)

    assert "Possible origin text." in parsed
    assert "Birth text." in parsed
    assert "Hercules text." in parsed
    assert "Minerva and Ulysses" in parsed
    assert "Worship in Rome and Italy" in parsed
    assert "Should be dropped." not in parsed
    assert "References" not in parsed


def test_plain_section_titles_are_treated_as_headings() -> None:
    parser = WikipediaParser()
    markdown = "\n".join(
        [
            "**Minerva** is a goddess.",
            "",
            "Titoli e ruoli",
            "",
            "Kept text.",
            "",
            "Note",
            "",
            "Should be dropped.",
        ]
    )

    parsed = parser.parse("https://it.wikipedia.org/wiki/Minerva", markdown)

    assert "Kept text." in parsed
    assert "Should be dropped." not in parsed


def test_noise_and_links_are_cleaned() -> None:
    parser = WikipediaParser()
    markdown = "\n".join(
        [
            "Jump to content",
            "Contents move to sidebar hide",
            "Text with [citation][12] and a [link](https://example.com).",
            "* [ 1 Etymology ](#Etymology)",
            "Retrieved from \"https://example.com\"",
        ]
    )

    parsed = parser.parse("https://en.wikipedia.org/wiki/BabelNet", markdown)

    assert parsed == "Text with and a link."
