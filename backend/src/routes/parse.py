"""Route handler for POST /parse."""

from fastapi import APIRouter, HTTPException

from ..lib import (
    assert_supported_domain,
    domain_of,
    fetch_page,
    fetch_page_from_html,
    get_parser_for_url,
)
from ..lib.db import queries
from ..schemas import ParseRequest, ParseResponse

router = APIRouter()


@router.post("/parse", response_model=ParseResponse)
async def parse(body: ParseRequest):
    """Parse a URL using either the live web (default) or the local DB.

    If ``local`` is True the HTML is read from the ``web_resources`` table;
    otherwise the page is crawled live.
    """
    if body.local:
        return await _parse_local(body.url)
    return await _parse_live(body.url)


async def _parse_live(url: str) -> ParseResponse:
    """Crawl the URL live and run it through the domain parser."""
    domain = domain_of(url)
    assert_supported_domain(domain)
    try:
        page = await fetch_page(url)
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error))
    parsed_text = get_parser_for_url(url).parse(url, page.markdown_text)
    return ParseResponse(
        url=url,
        domain=domain,
        title=page.title,
        html_text=page.html_text,
        parsed_text=parsed_text,
    )


async def _parse_local(url: str) -> ParseResponse:
    """Read the stored HTML from the DB and run it through the domain parser."""
    domain = domain_of(url)
    assert_supported_domain(domain)
    resource = queries.get_resource(url)
    if resource is None:
        raise HTTPException(status_code=404, detail=f"URL not found in DB: {url}")
    try:
        page = await fetch_page_from_html(url, resource.html_text)
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error))
    parsed_text = get_parser_for_url(url).parse(url, page.markdown_text)
    return ParseResponse(
        url=url,
        domain=domain,
        title=page.title or resource.title,
        html_text=resource.html_text,
        parsed_text=parsed_text,
    )
