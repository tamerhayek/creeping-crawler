"""Route handlers for gold standard endpoints."""

import asyncio

from fastapi import APIRouter, HTTPException, Query

from ..lib import (
    assert_supported_domain,
    build_gold_entry,
    domain_of,
    get_available_urls,
    get_urls_for_domain,
    load_gold_text,
)
from ..schemas import (
    FullGoldStandardResponse,
    GoldStandardEntry,
    GoldTextResponse,
    GsUrlsResponse,
)

router = APIRouter()


@router.get("/gold_standard", response_model=GoldStandardEntry)
async def gold_standard(url: str = Query(...)):
    """Return the gold standard entry for a URL, including a freshly crawled html_text."""
    assert_supported_domain(domain_of(url))
    return await build_gold_entry(url)


@router.get("/full_gold_standard", response_model=FullGoldStandardResponse)
async def full_gold_standard(domain: str = Query(...)):
    """Return all gold standard entries for a domain, crawling each URL concurrently."""
    assert_supported_domain(domain)
    urls = get_urls_for_domain(domain)
    entries = await asyncio.gather(*[build_gold_entry(url) for url in urls])
    return FullGoldStandardResponse(gold_standard=list(entries))


@router.get("/gs_urls", response_model=GsUrlsResponse)
def gs_urls():
    """Return all URLs present in the gold standard."""
    return GsUrlsResponse(urls=get_available_urls())


@router.get("/gold_text", response_model=GoldTextResponse)
def gold_text(url: str = Query(...)):
    """Return the stored gold text for a URL without crawling the live page."""
    assert_supported_domain(domain_of(url))
    text = load_gold_text(url)
    if text is None:
        raise HTTPException(status_code=404, detail=f"URL not found in gold standard: {url}")
    return GoldTextResponse(url=url, gold_text=text)
