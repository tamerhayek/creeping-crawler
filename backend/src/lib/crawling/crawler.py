"""Web crawling via Crawl4AI.

Fetches a page by URL (or from raw HTML) and returns a PageContent with
the page title, raw HTML, and converted markdown.
"""

import re
from dataclasses import dataclass

from crawl4ai import AsyncWebCrawler

from .configs.registry import config_for as _config_for


@dataclass
class PageContent:
    """Result returned by the crawler for a single page."""

    title: str
    html_text: str       # raw HTML of the page
    markdown_text: str   # markdown converted from the raw HTML


def _title(html: str, metadata: dict) -> str:
    """Extract the page title from Crawl4AI metadata or the raw HTML <title> tag."""
    title = (metadata or {}).get("title", "")
    if not title:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = m.group(1).strip() if m else ""
    return title


async def fetch_page(url: str) -> PageContent:
    """Crawl a URL and return its title, raw HTML, and markdown.

    Raises:
        RuntimeError: if Crawl4AI reports a failed crawl.
    """
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=_config_for(url))

    if not result.success:
        raise RuntimeError(f"Crawl failed for {url}: {result.error_message}")

    return PageContent(
        title=_title(result.html, result.metadata),
        html_text=result.html,
        markdown_text=result.markdown,
    )


async def fetch_page_from_html(url: str, html_text: str) -> PageContent:
    """Process a raw HTML string through Crawl4AI as if it were fetched from url.

    Uses Crawl4AI's raw: scheme so the domain-specific config still applies.

    Raises:
        RuntimeError: if Crawl4AI fails to process the HTML.
    """
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=f"raw:{html_text}", config=_config_for(url))

    if not result.success:
        raise RuntimeError(f"HTML processing failed: {result.error_message}")

    return PageContent(
        title=_title(html_text, result.metadata),
        html_text=html_text,
        markdown_text=result.markdown,
    )
