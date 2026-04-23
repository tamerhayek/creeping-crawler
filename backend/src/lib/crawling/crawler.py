"""Web crawling via Crawl4AI.

Architecture B: Crawl4AI produces both the raw HTML and the markdown.
  - html_text  = result.html  (always full raw HTML, unaffected by config filters)
  - markdown_text = result.markdown (filtered by CrawlerRunConfig, input to parsers)

To add a crawl config for a new domain, add an entry to DOMAIN_CONFIGS.
"""

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig


@dataclass
class PageContent:
    """Result of a crawl: title, raw HTML, and Crawl4AI-generated markdown."""

    title: str
    html_text: str      # raw full HTML — for display and POST re-parsing
    markdown_text: str  # Crawl4AI markdown (filtered by config) — input to parsers


DOMAIN_CONFIGS: dict[str, CrawlerRunConfig] = {
    "it.wikipedia.org": CrawlerRunConfig(
        magic=True,
        excluded_tags=["style", "script", "link"],
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
    ),
    "www.espn.com": CrawlerRunConfig(
        magic=True,
        excluded_tags=["style", "script", "link"],
        excluded_selector=(
            "nav, header, footer, aside, "
            ".ad-slot, .ad-300, "
            "[class*='scoreboard'], [class*='Scoreboard'], "
            "[class*='promo'], [class*='Promo'], "
            "[class*='related'], [class*='Related'], "
            "[class*='share'], [class*='social']"
        ),
        remove_forms=True,
    ),
    "www.xe.com": CrawlerRunConfig(
        magic=True,
        excluded_tags=["style", "script", "link"],
        excluded_selector=(
            "table, "
            "nav, header, footer, "
            "#__next > header, #__next > footer, "
            "a[href*='signup'], a[href*='register'], "
            ".breadcrumb, "
            "[class*='related'], [class*='Related'], "
            "[class*='cta'], [class*='banner'], "
            "[class*='footnote'], [class*='citation'], "
            "hr ~ *"
        ),
        remove_forms=True,
    ),
    "www.cnbc.com": CrawlerRunConfig(
        magic=True,
        excluded_tags=["style", "script", "link"],
        excluded_selector=(
            "nav, header, footer, aside, "
            "[data-slot], [data-ad], "
            ".nav-menu, .advertisement, "
            "[class*='related'], [class*='Related'], "
            "[class*='newsletter'], [class*='Newsletter']"
        ),
        remove_forms=True,
    ),
}

_DEFAULT_CONFIG = CrawlerRunConfig(magic=True)


def _run_config_for(url: str) -> CrawlerRunConfig:
    netloc = urlparse(url).netloc.lower()
    return DOMAIN_CONFIGS.get(netloc, _DEFAULT_CONFIG)


def _extract_markdown(result) -> str:
    """Return the raw markdown string from a CrawlResult (handles v0.4+ objects)."""
    md = result.markdown
    if md is None:
        return ""
    if hasattr(md, "raw_markdown"):
        return md.raw_markdown or ""
    return str(md)


def _extract_title(html: str, metadata: dict) -> str:
    """Return page title from metadata, falling back to <title> tag in raw HTML."""
    title = (metadata or {}).get("title", "")
    if not title and html:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = m.group(1).strip() if m else ""
    return title


async def fetch_page(url: str) -> PageContent:
    """Crawl a URL and return title, raw HTML, and Crawl4AI markdown.

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

    html_text = result.html or ""
    markdown_text = _extract_markdown(result)
    return PageContent(
        title=_extract_title(html_text, result.metadata),
        html_text=html_text,
        markdown_text=markdown_text,
    )


async def fetch_page_from_html(url: str, html_text: str) -> PageContent:
    """Convert a raw HTML string to markdown via Crawl4AI (raw: prefix).

    Applies the same domain CrawlerRunConfig as a real crawl so that
    excluded_selector/excluded_tags filter the markdown output.
    html_text is preserved as-is for display.

    Raises:
        RuntimeError: if Crawl4AI fails to process the HTML.
    """
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=f"raw:{html_text}",
                config=_run_config_for(url),
            )
    except Exception as e:
        raise RuntimeError(f"HTML processing failed: {e}")

    if not result.success:
        raise RuntimeError(f"HTML processing failed: {result.error_message}")

    markdown_text = _extract_markdown(result)
    return PageContent(
        title=_extract_title(html_text, result.metadata),
        html_text=html_text,
        markdown_text=markdown_text,
    )
