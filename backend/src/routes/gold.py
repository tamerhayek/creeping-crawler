"""Route handlers for gold standard endpoints."""

import asyncio

from fastapi import APIRouter, HTTPException, Query

from ..lib import (
    assert_supported_domain,
    domain_of,
    fetch_page_for_url,
    get_available_urls,
    get_entry_for_url,
    get_urls_for_domain,
    load_gold_text,
)
from ..schemas import (
    FullGoldStandardResponse,
    GoldStandardResponse,
    GoldTextResponse,
    GsUrlsResponse,
)

router = APIRouter()


async def _build_gold_entry(url: str) -> GoldStandardResponse:
    entry = get_entry_for_url(url)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"URL not found in gold standard: {url}")
    try:
        page = await fetch_page_for_url(url)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return GoldStandardResponse(
        url=url,
        domain=domain_of(url),
        title=page.title,
        html_text=page.html_text,
        gold_text=entry.get("gold_text", ""),
    )


@router.get("/gold_standard", response_model=GoldStandardResponse)
async def gold_standard(url: str = Query(...)):
    """Return the gold standard entry for a URL, including a freshly crawled html_text."""
    assert_supported_domain(domain_of(url))
    return await _build_gold_entry(url)


@router.get("/full_gold_standard", response_model=FullGoldStandardResponse)
async def full_gold_standard(domain: str = Query(...)):
    """Return all gold standard entries for a domain, crawling each URL concurrently."""
    assert_supported_domain(domain)
    urls = get_urls_for_domain(domain)
    entries = await asyncio.gather(*[_build_gold_entry(url) for url in urls])
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
