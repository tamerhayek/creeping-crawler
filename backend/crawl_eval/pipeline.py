from dataclasses import dataclass
from pathlib import Path

from .crawler import fetch_markdown
from .gold import gold_sample_path_for_url, load_sample_tokens
from .metrics import TokenMetrics, calculate_metrics
from .parsers import get_parser_for_url
from .tokens import extract_unique_tokens


@dataclass(frozen=True)
class EvaluationResult:
    url: str
    parser_name: str
    sample_path: Path
    extracted_text: str
    extracted_tokens: set[str]
    sample_tokens: set[str]
    metrics: TokenMetrics


async def crawl_and_evaluate(url: str, sample_path: Path | None = None) -> EvaluationResult:
    resolved_sample_path = sample_path or gold_sample_path_for_url(url)
    parser = get_parser_for_url(url)

    markdown = await fetch_markdown(url)
    extracted_text = parser.parse(url, markdown)
    extracted_tokens = extract_unique_tokens(extracted_text)
    sample_tokens = load_sample_tokens(resolved_sample_path)
    metrics = calculate_metrics(extracted_tokens, sample_tokens)

    return EvaluationResult(
        url=url,
        parser_name=parser.__class__.__name__,
        sample_path=resolved_sample_path,
        extracted_text=extracted_text,
        extracted_tokens=extracted_tokens,
        sample_tokens=sample_tokens,
        metrics=metrics,
    )
