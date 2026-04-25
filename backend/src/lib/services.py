"""Shared business logic used across multiple routes."""

from urllib.parse import urlparse

from fastapi import HTTPException

from .crawling.crawler import fetch_page, fetch_page_from_html, PageContent
from .evaluation.metrics import calculate_content_metrics, calculate_token_level_metrics
from .gold_standard.gold import get_entry_for_url, load_gold_text
from .gold_standard.urls import is_supported_domain
from ..schemas import GoldStandardEntry, SimilarityEval, TokenLevelEval


async def fetch_page_for_url(url: str) -> PageContent:
    """Fetch a page using the stored HTML from the gold standard if available, else crawl live."""
    entry = get_entry_for_url(url)
    if entry and entry.get("html_text"):
        page = await fetch_page_from_html(url, entry["html_text"])
        if page.markdown_text:
            return page
    return await fetch_page(url)


def domain_of(url: str) -> str:
    return urlparse(url).netloc


def assert_supported_domain(domain: str) -> None:
    if not is_supported_domain(domain):
        raise HTTPException(status_code=400, detail=f"Unsupported domain: {domain}")


def compute_token_level_eval(parsed_text: str, gold_text: str) -> TokenLevelEval:
    """Compute precision, recall, and F1 between parsed and gold text (set-based)."""
    m = calculate_token_level_metrics(parsed_text, gold_text)
    return TokenLevelEval(precision=m.precision, recall=m.recall, f1=m.f1)


def compute_similarity_eval(parsed_text: str, gold_text: str) -> SimilarityEval:
    """Compute token-count-based metrics (cosine, jaccard, excess_ratio) between parsed and gold text."""
    m = calculate_content_metrics(parsed_text, gold_text)
    return SimilarityEval(cosine=m.cosine, jaccard=m.jaccard, excess_ratio=m.excess_ratio)


async def build_gold_entry(url: str) -> GoldStandardEntry:
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
