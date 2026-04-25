"""Shared business logic used across multiple routes.

Contains domain validation, token-level evaluation, and gold standard entry building.
All functions that need to raise HTTP errors live here so routes stay thin.
"""

from urllib.parse import urlparse

from fastapi import HTTPException

from .crawling.crawler import fetch_page, fetch_page_from_html, PageContent
from .evaluation.metrics import calculate_metrics
from .evaluation.tokens import extract_unique_tokens, strip_markdown
from .gold_standard.gold import get_entry_for_url, load_gold_text
from .gold_standard.urls import is_supported_domain
from ..schemas import GoldStandardEntry, TokenLevelEval

async def fetch_page_for_url(url: str) -> PageContent:
    """Fetch a page using the stored HTML from the gold standard if available, else crawl live.

    Tries the GS snapshot first. Falls back to a live crawl if the snapshot
    produces empty markdown (e.g. conversion failure on very large HTML).
    """
    entry = get_entry_for_url(url)
    if entry and entry.get("html_text"):
        page = await fetch_page_from_html(url, entry["html_text"])
        if page.markdown_text:
            return page
        # Snapshot produced empty markdown — fall back to live crawl
    return await fetch_page(url)


def domain_of(url: str) -> str:
    """Extract the netloc (domain) from a URL."""
    return urlparse(url).netloc

def assert_supported_domain(domain: str) -> None:
    """Raise HTTP 400 if the domain has no gold standard entries."""
    if not is_supported_domain(domain):
        raise HTTPException(status_code=400, detail=f"Unsupported domain: {domain}")

def compute_token_eval(parsed_text: str, gold_text: str) -> TokenLevelEval:
    """Compute token-level precision, recall, and F1 between parsed and gold text.

    Markdown is stripped from parsed_text before tokenization so that
    formatting characters do not inflate or deflate the scores.
    """
    extracted_tokens = extract_unique_tokens(strip_markdown(parsed_text))
    sample_tokens = extract_unique_tokens(gold_text)
    metrics = calculate_metrics(extracted_tokens, sample_tokens)
    return TokenLevelEval(
        precision=metrics.precision,
        recall=metrics.recall,
        f1=metrics.f1,
    )

async def build_gold_entry(url: str) -> GoldStandardEntry:
    """Crawl a URL and combine the live page with its stored gold standard entry.

    Raises:
        HTTPException 404: if the URL is not in the gold standard.
        HTTPException 503: if the page cannot be crawled.
    """
    entry = get_entry_for_url(url)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"URL not found in gold standard: {url}")

    try:
        page = await fetch_page_for_url(url)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return GoldStandardEntry(
        url=url,
        domain=domain_of(url),
        title=page.title,
        html_text=page.html_text,
        gold_text=entry.get("gold_text", ""),
    )
