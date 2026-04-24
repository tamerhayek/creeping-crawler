"""Crawler config for it.wikipedia.org."""

from crawl4ai import CrawlerRunConfig

CONFIG = CrawlerRunConfig(
    magic=True,
    excluded_tags=["style", "script", "link", "meta"],
    excluded_selector=(
        "table.infobox, table.sinottico, "
        ".shortdescription, .hatnote, "
        ".toc, "
        ".navbox, .vertical-navbox, "
        ".metadata, .mw-editsection, "
        ".reflist, .mw-references, sup.reference, "
        "#catlinks"
    ),
    remove_forms=True,
)
