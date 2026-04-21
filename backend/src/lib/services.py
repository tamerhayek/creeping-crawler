from urllib.parse import urlparse

from fastapi import HTTPException

from .crawler import fetch_page
from .gold import gold_sample_path_for_url, load_sample_text
from .metrics import calculate_metrics
from .tokens import extract_unique_tokens, strip_markdown
from .urls import is_supported_domain
from ..schemas import GoldStandardEntry, TokenLevelEval


def domain_of(url: str) -> str:
    return urlparse(url).netloc


def assert_supported_domain(domain: str) -> None:
    if not is_supported_domain(domain):
        raise HTTPException(status_code=400, detail=f"Unsupported domain: {domain}")


def compute_token_eval(parsed_text: str, gold_text: str) -> TokenLevelEval:
    extracted_tokens = extract_unique_tokens(strip_markdown(parsed_text))
    sample_tokens = extract_unique_tokens(gold_text)
    metrics = calculate_metrics(extracted_tokens, sample_tokens)
    return TokenLevelEval(
        precision=metrics.precision,
        recall=metrics.recall,
        f1=metrics.f1,
    )


async def build_gold_entry(url: str) -> GoldStandardEntry:
    domain = domain_of(url)
    sample_path = gold_sample_path_for_url(url)
    gold_text = load_sample_text(sample_path)

    try:
        page = await fetch_page(url)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return GoldStandardEntry(
        url=url,
        domain=domain,
        title=page.title,
        html_text=page.html_text,
        gold_text=gold_text,
    )
