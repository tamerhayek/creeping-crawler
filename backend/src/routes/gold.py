"""Route handlers for gold standard endpoints."""

from fastapi import APIRouter, HTTPException, Query

from ..lib import (
    assert_supported_domain,
    domain_of,
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


def _entry_to_response(entry: dict) -> GoldStandardResponse:
    return GoldStandardResponse(
        url=entry["url"],
        domain=entry["domain"],
        title=entry.get("title", ""),
        html_text=entry.get("html_text", ""),
        gold_text=entry.get("gold_text", ""),
    )


@router.get("/gold_standard", response_model=GoldStandardResponse)
def gold_standard(url: str = Query(...)):
    """Return the gold standard entry for a URL, read directly from the GS JSON."""
    assert_supported_domain(domain_of(url))
    entry = get_entry_for_url(url)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"URL not found in gold standard: {url}")
    return _entry_to_response(entry)


@router.get("/full_gold_standard", response_model=FullGoldStandardResponse)
def full_gold_standard(domain: str = Query(...)):
    """Return all gold standard entries for a domain, read directly from the GS JSON."""
    assert_supported_domain(domain)
    urls = get_urls_for_domain(domain)
    entries = []
    for url in urls:
        entry = get_entry_for_url(url)
        if entry is not None:
            entries.append(_entry_to_response(entry))
    return FullGoldStandardResponse(gold_standard=entries)


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
