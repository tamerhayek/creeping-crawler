"""Web crawling via Crawl4AI.

Fetches a page by URL (or from raw HTML) and returns a PageContent with
the page title, raw HTML, and converted markdown.
"""

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig


@dataclass
class PageContent:
    """Result returned by the crawler for a single page."""

    title: str
    html_text: str       # raw HTML of the page
    markdown_text: str   # markdown converted from the raw HTML


# Domain-specific crawler configs.
# Add an entry here to customise crawling behaviour for a domain.
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
        excluded_tags=["style", "script", "link", "meta", "noscript"],
        excluded_selector=(
            # Global navigation & menus
            "#GlobalNavigation, "
            "[class*='CNBCGlobalNav'], "
            "[class*='nav-menu-'], "
            # Account / sign-in / sign-up
            "[class*='account-menu'], "
            "[class*='SignInMenu'], "
            "[class*='SignUpMenu'], "
            # Skip / jump links
            "[class*='JumpLink'], "
            # Watch-live button
            "[class*='WatchLive'], "
            # Cookie consent (OneTrust)
            "#onetrust-consent-sdk, #onetrust-banner-sdk, "
            "#onetrust-pc-sdk, .otFlat, .ot-iab-2, "
            # Article eyebrow (category breadcrumb) and publish date
            "[class*='ArticleHeader-eyebrow'], "
            "[class*='ArticleHeader-time'], "
            # Author info block
            "[class*='Author-author'], "
            "[class*='ArticleHeader-authorAndShareInline'], "
            # Inline video embeds
            "[class*='InlineVideo'], "
            "[class*='PlaceHolder-wrapper'], "
            # Inline image embeds
            "[class*='InlineImage-imageEmbed'], "
            # Stock ticker / related quotes widget and inline ticker buttons
            ".RelatedQuotes-relatedQuotes, "
            "[class*='QuoteInBody-inlineButton'], "
            # "Choose CNBC as your preferred source" banner
            "[class*='googlePreferredSourceContainer'], "
            # Special-report topic navigation
            "[class*='PageHeaderWithTuneInText'], "
            # Transporter / recommended-articles sections
            "[class*='TransporterSection'], "
            "[class*='SectionWrapper'], "
            # Global footer
            "#GlobalFooter, [class*='CNBCFooter']"
        ),
        remove_forms=True,
    ),
}

_DEFAULT_CONFIG = CrawlerRunConfig(magic=True)


def _config_for(url: str) -> CrawlerRunConfig:
    """Return the crawler config for the given URL's domain."""
    return DOMAIN_CONFIGS.get(urlparse(url).netloc.lower(), _DEFAULT_CONFIG)


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
