import asyncio

from fastapi import APIRouter, HTTPException, Query

from ..lib.crawler import fetch_page
from ..lib.gold import load_gold_text
from ..lib.parsers import get_parser_for_url
from ..lib.services import assert_supported_domain, compute_token_eval
from ..lib.urls import get_urls_for_domain
from ..schemas import EvaluateRequest, EvaluateResponse, TokenLevelEval

router = APIRouter()


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate(body: EvaluateRequest):
    token_eval = compute_token_eval(body.parsed_text, body.gold_text)
    return EvaluateResponse(token_level_eval=token_eval)


@router.get("/full_gs_eval", response_model=EvaluateResponse)
async def full_gs_eval(domain: str = Query(...)):
    assert_supported_domain(domain)
    urls = get_urls_for_domain(domain)

    async def _eval_url(url: str) -> TokenLevelEval:
        gold_text = load_gold_text(url)
        if not gold_text:
            raise HTTPException(status_code=404, detail=f"No gold text for: {url}")
        try:
            page = await fetch_page(url)
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
        parser = get_parser_for_url(url)
        parsed_text = parser.parse(url, page.html_text)
        return compute_token_eval(parsed_text, gold_text)

    evals = await asyncio.gather(*[_eval_url(url) for url in urls])
    n = len(evals)
    return EvaluateResponse(
        token_level_eval=TokenLevelEval(
            precision=sum(e.precision for e in evals) / n,
            recall=sum(e.recall for e in evals) / n,
            f1=sum(e.f1 for e in evals) / n,
        )
    )
