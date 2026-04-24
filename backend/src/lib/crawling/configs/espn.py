"""Crawler config for www.espn.com."""

from crawl4ai import CrawlerRunConfig

CONFIG = CrawlerRunConfig(
    magic=True,
    excluded_tags=["style", "script", "link", "meta"],
    excluded_selector="",
    remove_forms=True,
)
