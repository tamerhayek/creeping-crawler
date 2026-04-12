from crawl_eval.parsers.wikipedia import WikipediaParser


def test_excludes_reference_sections() -> None:
    parser = WikipediaParser()
    markdown = "\n".join(
        [
            "# Minerva",
            "Lead paragraph.",
            "",
            "## History",
            "Some history.",
            "",
            "## References",
            "Should be dropped.",
            "",
            "## External links",
            "Should also be dropped.",
        ]
    )

    parsed = parser.parse("https://en.wikipedia.org/wiki/Minerva", markdown)

    assert "Lead paragraph." in parsed
    assert "History" in parsed
    assert "Some history." in parsed
    assert "References" not in parsed
    assert "Should be dropped." not in parsed


def test_removes_simple_reference_markers() -> None:
    parser = WikipediaParser()
    markdown = "# BabelNet\nText with citation[12]."

    parsed = parser.parse("https://en.wikipedia.org/wiki/BabelNet", markdown)

    assert parsed == "BabelNet\nText with citation."
