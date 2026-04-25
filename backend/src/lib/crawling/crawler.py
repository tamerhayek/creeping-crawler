"""Web crawling via Crawl4AI.

Fetches a page by URL (or from raw HTML) and returns a PageContent with
the page title, raw HTML, and converted markdown.
"""

import re
from dataclasses import dataclass

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

from .configs.registry import config_for as _config_for


def _html_only_config(url: str) -> CrawlerRunConfig:
    """Return a browser-free config for processing already-fetched HTML.

    Keeps domain-specific extraction filters (excluded_tags, excluded_selector,
    remove_forms) but drops magic and any other flag that would trigger
    Playwright, since we already have the HTML and only need the
    HTML-to-markdown conversion pipeline.
    """
    base = _config_for(url)
    return CrawlerRunConfig(
        excluded_tags=base.excluded_tags,
        excluded_selector=base.excluded_selector,
        remove_forms=base.remove_forms,
    )


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
    """Convert a stored HTML string to markdown using Crawl4AI's fast path.

    Passes the HTML via the raw: scheme with a browser-free config so that
    Crawl4AI skips Playwright and runs only the HTML-to-markdown pipeline.
    Domain-specific extraction filters (excluded_tags, excluded_selector, etc.)
    are preserved; magic/JS execution is intentionally disabled since the HTML
    is already available and doesn't need rendering.

    Raises:
        RuntimeError: if Crawl4AI fails to process the HTML.
    """
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=f"raw:{html_text}", config=_html_only_config(url))

    if not result.success:
        raise RuntimeError(f"HTML processing failed: {result.error_message}")

    return PageContent(
        title=_title(html_text, result.metadata),
        html_text=html_text,
        markdown_text=result.markdown,
    )
