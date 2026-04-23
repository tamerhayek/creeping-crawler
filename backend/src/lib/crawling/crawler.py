import re
from dataclasses import dataclass
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

@dataclass
class PageContent:
    title: str
    html_text: str
    markdown_text: str

# --- Domain-specific configs ---
# Add an entry here to customize crawling for a domain.
# Domains not listed fall back to _DEFAULT_CONFIG.
DOMAIN_CONFIGS: dict[str, CrawlerRunConfig] = {
    "it.wikipedia.org": CrawlerRunConfig(
        magic=True,
        excluded_tags=["style", "script", "link", "meta"],
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
        excluded_tags=["style", "script", "link", "meta"],
        excluded_selector="",
        remove_forms=True,
    ),
    "www.xe.com": CrawlerRunConfig(
        magic=True,
        excluded_tags=["style", "script", "link", "meta"],
        excluded_selector="",
        remove_forms=True,
    ),
    "www.cnbc.com": CrawlerRunConfig(
        magic=True,
        excluded_tags=["style", "script", "link", "meta"],
        excluded_selector="",
        remove_forms=True,
    ),
}

_DEFAULT_CONFIG = CrawlerRunConfig(magic=True)

def _config_for(url: str) -> CrawlerRunConfig:
    return DOMAIN_CONFIGS.get(urlparse(url).netloc.lower(), _DEFAULT_CONFIG)

def _title(html: str, metadata: dict) -> str:
    title = (metadata or {}).get("title", "")
    if not title:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = m.group(1).strip() if m else ""
    return title

async def fetch_page(url: str) -> PageContent:
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
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=f"raw:{html_text}", config=_config_for(url))

    if not result.success:
        raise RuntimeError(f"HTML processing failed: {result.error_message}")

    return PageContent(
        title=_title(html_text, result.metadata),
        html_text=html_text,
        markdown_text=result.markdown,
    )
