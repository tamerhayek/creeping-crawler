"""Web crawling via Crawl4AI.

Fetches pages and returns their raw markdown content and metadata.
The markdown is used as input for domain-specific parsers.
"""

from dataclasses import dataclass
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig


@dataclass
class PageContent:
    """Holds the result of a crawl: page title and raw markdown text."""

    title: str
    html_text: str  # raw markdown produced by Crawl4AI — input to the parser


def _run_config_for(url: str) -> CrawlerRunConfig:
    """Return a domain-specific CrawlerRunConfig.

    Wikipedia pages use a targeted CSS selector to exclude navigation,
    infoboxes, references, and other non-content elements before crawling.
    All other domains use the default magic-mode config.
    """
    if urlparse(url).netloc.endswith("wikipedia.org"):
        return CrawlerRunConfig(
            magic=True,
            css_selector=".mw-parser-output > p, .mw-parser-output > section",
            excluded_tags=["style", "script", "link", "meta"],
            excluded_selector=(
                "table.infobox, .shortdescription, .hatnote, .toc, "
                ".navbox, .vertical-navbox, .metadata, .mw-editsection, "
                ".reflist, #catlinks"
            ),
            remove_forms=True,
        )
    return CrawlerRunConfig(magic=True)


async def fetch_page(url: str) -> PageContent:
    """Crawl a URL and return its title and raw markdown.

    Raises:
        RuntimeError: if the crawl fails or the URL is unreachable.
    """
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=_run_config_for(url))
    except Exception as e:
        raise RuntimeError(f"Crawl failed for {url}: {e}")

    if not result.success:
        raise RuntimeError(f"Crawl failed for {url}: {result.error_message}")

    title = (result.metadata or {}).get("title", "")
    html_text = result.markdown.raw_markdown if result.markdown else ""
    return PageContent(title=title, html_text=html_text)
