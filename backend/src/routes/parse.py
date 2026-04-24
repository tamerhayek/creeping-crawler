"""Route handlers for GET /parse and POST /parse."""

from fastapi import APIRouter, HTTPException, Query

from ..lib import assert_supported_domain, domain_of, fetch_page, fetch_page_from_html, get_parser_for_url
from ..schemas import ParseRequest, ParseResponse

router = APIRouter()


@router.get("/parse", response_model=ParseResponse)
async def parse_get(url: str = Query(...)):
    """Crawl a URL, apply the domain parser, and return the parsed text."""
    domain = domain_of(url)
    assert_supported_domain(domain)

    try:
        page = await fetch_page(url)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    parser = get_parser_for_url(url)
    parsed_text = parser.parse(url, page.markdown_text)

    return ParseResponse(
        url=url,
        domain=domain,
        title=page.title,
        html_text=page.html_text,
        parsed_text=parsed_text,
    )


@router.post("/parse", response_model=ParseResponse)
async def parse_post(body: ParseRequest):
    """Process a provided HTML string, apply the domain parser, and return the parsed text."""
    domain = domain_of(body.url)
    assert_supported_domain(domain)

    try:
        page = await fetch_page_from_html(body.url, body.html_text)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    parser = get_parser_for_url(body.url)
    parsed_text = parser.parse(body.url, page.markdown_text)

    return ParseResponse(
        url=body.url,
        domain=domain,
        title=page.title,
        html_text=body.html_text,
        parsed_text=parsed_text,
    )
