import re
from dataclasses import dataclass

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

@dataclass
class PageContent:
    title: str
    html_text: str
    markdown_text: str


_CONFIG = CrawlerRunConfig(magic=True)

async def fetch_page(url: str) -> PageContent:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=_CONFIG)

    if not result.success:
        raise RuntimeError(f"Crawl failed for {url}: {result.error_message}")

    title = (result.metadata or {}).get("title", "")
    if not title:
        m = re.search(r"<title[^>]*>(.*?)</title>", result.html, re.IGNORECASE | re.DOTALL)
        title = m.group(1).strip() if m else ""

    return PageContent(title=title, html_text=result.html, markdown_text=result.markdown)

async def fetch_page_from_html(url: str, html_text: str) -> PageContent:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=f"raw:{html_text}", config=_CONFIG)

    if not result.success:
        raise RuntimeError(f"HTML processing failed: {result.error_message}")

    m = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    title = m.group(1).strip() if m else ""

    return PageContent(title=title, html_text=html_text, markdown_text=result.markdown)
