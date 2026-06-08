"""Route handlers for evaluation endpoints."""

import asyncio

from fastapi import APIRouter, Query

from ..lib import (
    assert_supported_domain,
    calculate_content_metrics,
    calculate_token_level_metrics,
    fetch_page_from_html,
    get_parser_for_url,
)
from ..lib.db import queries
from ..lib.llm import evaluate_with_judge
from ..schemas import (
    EvaluateRequest,
    EvaluateResponse,
    FullGsEvalResponse,
    JudgeEvalResponse,
    SimilarityEval,
    TokenLevelEval,
)

router = APIRouter()


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate(body: EvaluateRequest):
    """Compute token-level and similarity metrics for a parsed/gold text pair."""
    token_level = calculate_token_level_metrics(body.parsed_text, body.gold_text)
    similarity = calculate_content_metrics(body.parsed_text, body.gold_text)
    return EvaluateResponse(
        token_level_eval=TokenLevelEval(
            precision=token_level.precision,
            recall=token_level.recall,
            f1=token_level.f1,
        ),
        similarity_eval=SimilarityEval(
            cosine=similarity.cosine,
            jaccard=similarity.jaccard,
            excess_ratio=similarity.excess_ratio,
        ),
    )


@router.post("/evaluate_judge", response_model=JudgeEvalResponse)
def evaluate_judge(body: EvaluateRequest):
    """Score the parsed text against the gold text using the LLM judge."""
    result = evaluate_with_judge(body.parsed_text, body.gold_text)
    return JudgeEvalResponse(
        model_name=result.model_name,
        judge_score=result.judge_score,
        judge_feedback=result.judge_feedback,
    )


@router.get("/full_gs_eval", response_model=FullGsEvalResponse)
async def full_gs_eval(domain: str = Query(...)):
    """Average all quantitative and judge metrics across a domain's gold standard.

    Uses the HTML stored in the DB (no live crawl) so the evaluation is
    repeatable and not influenced by website changes.
    """
    assert_supported_domain(domain)
    entries = queries.get_entries_by_domain(domain)

    # Parse all entries in parallel: only the markdown conversion is async-bound.
    parsed_texts = await asyncio.gather(*[_parse_entry(entry) for entry in entries])

    token_level_results = []
    similarity_results = []
    judge_scores = []
    for entry, parsed_text in zip(entries, parsed_texts):
        token_level = calculate_token_level_metrics(parsed_text, entry.gold_text)
        similarity = calculate_content_metrics(parsed_text, entry.gold_text)
        # The judge is a blocking HTTP call to Ollama; run them sequentially
        # since Ollama serves one request at a time anyway.
        judge = evaluate_with_judge(parsed_text, entry.gold_text)

        token_level_results.append(token_level)
        similarity_results.append(similarity)
        judge_scores.append(judge.judge_score)

        # Cache per-URL results so /db_stats can read them without re-running
        # the parsers and the judge.
        queries.save_quantitative_eval(
            entry.url,
            token_level.precision, token_level.recall, token_level.f1,
            similarity.cosine, similarity.jaccard, similarity.excess_ratio,
        )
        queries.save_judge_eval(entry.url, judge.judge_score)

    count = len(entries)
    return FullGsEvalResponse(
        token_level_eval=TokenLevelEval(
            precision=sum(r.precision for r in token_level_results) / count,
            recall=sum(r.recall for r in token_level_results) / count,
            f1=sum(r.f1 for r in token_level_results) / count,
        ),
        similarity_eval=SimilarityEval(
            cosine=sum(r.cosine for r in similarity_results) / count,
            jaccard=sum(r.jaccard for r in similarity_results) / count,
            excess_ratio=sum(r.excess_ratio for r in similarity_results) / count,
        ),
        judge_score=sum(judge_scores) / count,
    )


async def _parse_entry(entry) -> str:
    """Re-parse a stored HTML through its domain parser."""
    page = await fetch_page_from_html(entry.url, entry.html_text)
    return get_parser_for_url(entry.url).parse(entry.url, page.markdown_text)
