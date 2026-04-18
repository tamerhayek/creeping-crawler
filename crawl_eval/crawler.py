from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def fetch_markdown(url: str) -> str:
    if urlparse(url).netloc.endswith("wikipedia.org"):
        run_config = CrawlerRunConfig(
            css_selector=".mw-parser-output > p, .mw-parser-output > section",
            excluded_tags=[
                "style",
                "script",
                "link",
                "meta",
                "table.infobox",
                ".shortdescription",
                ".hatnote",
                ".toc",
                ".navbox",
                ".vertical-navbox",
                ".metadata",
                ".mw-editsection",
                ".reflist",
                "#catlinks",
            ],
            remove_forms=True,
        )
    else:
        run_config = CrawlerRunConfig()

    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=run_config)
    except Exception:
        raise RuntimeError(f"Crawl failed for {url}")

    if not result.success:
        raise RuntimeError(f"Crawl failed for {url}: {result.error_message}")

    return result.markdown.raw_markdown if result.markdown else ""
