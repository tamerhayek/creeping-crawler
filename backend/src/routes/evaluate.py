"""Route handlers for evaluation endpoints."""

import asyncio

from fastapi import APIRouter, HTTPException, Query

from ..lib import (
    assert_supported_domain,
    compute_similarity_eval,
    compute_token_level_eval,
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
    return EvaluateResponse(
        token_level_eval=compute_token_level_eval(body.parsed_text, body.gold_text),
        similarity_eval=compute_similarity_eval(body.parsed_text, body.gold_text),
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
        return (
            compute_token_level_eval(parsed_text, gold_text),
            compute_similarity_eval(parsed_text, gold_text),
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
