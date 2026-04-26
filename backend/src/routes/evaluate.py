"""Route handlers for evaluation endpoints."""

import asyncio

from fastapi import APIRouter, HTTPException, Query

from ..lib import (
    assert_supported_domain,
    calculate_content_metrics,
    calculate_token_level_metrics,
    fetch_page_for_url,
    get_parser_for_url,
    get_urls_for_domain,
    load_gold_text,
)
from ..schemas import EvaluateRequest, EvaluateResponse, SimilarityEval, TokenLevelEval

router = APIRouter()


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate(body: EvaluateRequest):
    """Compute token-level and token-count evaluation metrics for a parsed/gold text pair."""
    tl = calculate_token_level_metrics(body.parsed_text, body.gold_text)
    sim = calculate_content_metrics(body.parsed_text, body.gold_text)
    return EvaluateResponse(
        token_level_eval=TokenLevelEval(precision=tl.precision, recall=tl.recall, f1=tl.f1),
        similarity_eval=SimilarityEval(cosine=sim.cosine, jaccard=sim.jaccard, excess_ratio=sim.excess_ratio),
    )


@router.get("/full_gs_eval", response_model=EvaluateResponse)
async def full_gs_eval(domain: str = Query(...)):
    """Crawl every URL for a domain, parse it, and return averaged evaluation scores."""
    assert_supported_domain(domain)
    urls = get_urls_for_domain(domain)

    async def _eval_url(url: str) -> tuple[TokenLevelEval, SimilarityEval]:
        gold_text = load_gold_text(url)
        if not gold_text:
            raise HTTPException(status_code=404, detail=f"No gold text for: {url}")
        try:
            page = await fetch_page_for_url(url)
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
        parsed_text = get_parser_for_url(url).parse(url, page.markdown_text)
        tl = calculate_token_level_metrics(parsed_text, gold_text)
        sim = calculate_content_metrics(parsed_text, gold_text)
        return (
            TokenLevelEval(precision=tl.precision, recall=tl.recall, f1=tl.f1),
            SimilarityEval(cosine=sim.cosine, jaccard=sim.jaccard, excess_ratio=sim.excess_ratio),
        )

    results = await asyncio.gather(*[_eval_url(url) for url in urls])
    token_level_evals, similarity_evals = zip(*results)
    n = len(results)

    return EvaluateResponse(
        token_level_eval=TokenLevelEval(
            precision=sum(e.precision for e in token_level_evals) / n,
            recall=sum(e.recall for e in token_level_evals) / n,
            f1=sum(e.f1 for e in token_level_evals) / n,
        ),
        similarity_eval=SimilarityEval(
            cosine=sum(e.cosine for e in similarity_evals) / n,
            jaccard=sum(e.jaccard for e in similarity_evals) / n,
            excess_ratio=sum(e.excess_ratio for e in similarity_evals) / n,
        ),
    )
