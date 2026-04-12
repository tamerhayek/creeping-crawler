from crawl4ai import AsyncWebCrawler


async def fetch_markdown(url: str) -> str:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)

    if not result.success:
        raise RuntimeError(f"Crawl failed for {url}: {result.error_message}")

    return result.markdown or ""
