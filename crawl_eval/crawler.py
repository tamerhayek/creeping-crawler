from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler

async def fetch_markdown(url: str) -> str:
    crawl_kwargs = {}
    if urlparse(url).netloc.endswith("wikipedia.org"):
        crawl_kwargs = {
            "css_selector": ".mw-parser-output > p, .mw-parser-output > section",
            "excluded_tags": [
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
            "remove_forms": True,
        }

    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, **crawl_kwargs)
    except Exception:
        raise RuntimeError(f"Crawl failed for {url}")

    if not result.success:
        raise RuntimeError(f"Crawl failed for {url}: {result.error_message}")

    return result.markdown or ""
