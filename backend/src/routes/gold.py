import asyncio

from fastapi import APIRouter, HTTPException, Query

from ..lib import (
    assert_supported_domain,
    build_gold_entry,
    domain_of,
    fetch_page,
    get_available_urls,
    get_entry_for_url,
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
    domain = domain_of(url)
    assert_supported_domain(domain)

    entry = get_entry_for_url(url)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"URL not found in gold standard: {url}")

    try:
        page = await fetch_page(url)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return GoldStandardEntry(
        url=url,
        domain=domain,
        title=page.title,
        html_text=page.html_text,
        gold_text=entry.get("gold_text", ""),
    )


@router.get("/full_gold_standard", response_model=FullGoldStandardResponse)
async def full_gold_standard(domain: str = Query(...)):
    assert_supported_domain(domain)
    urls = get_urls_for_domain(domain)
    entries = await asyncio.gather(*[build_gold_entry(url) for url in urls])
    return FullGoldStandardResponse(gold_standard=list(entries))


@router.get("/gs_urls", response_model=GsUrlsResponse)
def gs_urls():
    return GsUrlsResponse(urls=get_available_urls())


@router.get("/gold_text", response_model=GoldTextResponse)
def gold_text(url: str = Query(...)):
    assert_supported_domain(domain_of(url))
    text = load_gold_text(url)
    if text is None:
        raise HTTPException(status_code=404, detail=f"URL not found in gold standard: {url}")
    return GoldTextResponse(url=url, gold_text=text)
