"""Web crawling via Crawl4AI.

Fetches pages and returns their raw markdown content and metadata.
The markdown is used as input for domain-specific parsers.

To add a crawl config for a new domain, add an entry to DOMAIN_CONFIGS
using the domain suffix as key (e.g. "espn.com").
"""

from dataclasses import dataclass
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig


@dataclass
class PageContent:
    """Holds the result of a crawl: page title and raw markdown text."""

    title: str
    html_text: str  # raw markdown produced by Crawl4AI — input to the parser


# Registry of domain-specific crawl configurations.
# Keys are exact domain strings as they appear in domains.json.
# Only exact netloc matches are accepted — subdomains and variants are excluded.
DOMAIN_CONFIGS: dict[str, CrawlerRunConfig] = {
    "it.wikipedia.org": CrawlerRunConfig(
        magic=True,
        css_selector=".mw-parser-output > p, .mw-parser-output > section",
        excluded_tags=["style", "script", "link", "meta"],
        excluded_selector=(
            "table.infobox, .shortdescription, .hatnote, .toc, "
            ".navbox, .vertical-navbox, .metadata, .mw-editsection, "
            ".reflist, #catlinks"
        ),
        remove_forms=True,
    ),
    "espn.com": CrawlerRunConfig(
        magic=True,
        excluded_tags=["style", "script", "link", "meta"],
        remove_forms=True,
    ),
    "www.xe.com": CrawlerRunConfig(
        magic=True,
        excluded_tags=["style", "script", "link", "meta"],
        remove_forms=True,
    ),
    "www.cnbc.com": CrawlerRunConfig(
        magic=True,
        excluded_tags=["style", "script", "link", "meta"],
        remove_forms=True,
    ),
}

_DEFAULT_CONFIG = CrawlerRunConfig(magic=True)

def _run_config_for(url: str) -> CrawlerRunConfig:
    """Return the CrawlerRunConfig for the given URL's domain.

    Looks up the exact netloc in DOMAIN_CONFIGS.
    Falls back to a plain magic-mode config if the domain is not listed.
    """
    netloc = urlparse(url).netloc.lower()
    return DOMAIN_CONFIGS.get(netloc, _DEFAULT_CONFIG)


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
    html_text = result.html or ""
    return PageContent(title=title, html_text=html_text)
