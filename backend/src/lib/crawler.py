from dataclasses import dataclass
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig


@dataclass
class PageContent:
    title: str
    html_text: str  # raw markdown from crawl4ai — input to the parser


def _run_config_for(url: str) -> CrawlerRunConfig:
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


async def fetch_markdown(url: str) -> str:
    page = await fetch_page(url)
    return page.html_text
