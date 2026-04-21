from fastapi import APIRouter, HTTPException, Query

from ..lib import assert_supported_domain, domain_of, fetch_page, get_parser_for_url
from ..schemas import ParseResponse

router = APIRouter()

@router.get("/parse", response_model=ParseResponse)
async def parse(url: str = Query(...)):
    domain = domain_of(url)
    assert_supported_domain(domain)

    try:
        page = await fetch_page(url)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    parser = get_parser_for_url(url)
    parsed_text = parser.parse(url, page.html_text)

    return ParseResponse(
        url=url,
        domain=domain,
        title=page.title,
        html_text=page.html_text,
        parsed_text=parsed_text,
    )
