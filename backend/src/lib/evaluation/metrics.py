"""Evaluation metrics for token-level and token-count-level comparison.

token_level_eval  — operates on token *sets* (presence/absence)
token_count_eval  — operates on token *frequency vectors* (cosine similarity)

Both functions receive raw parsed_text and gold_text strings and handle
stripping/tokenization internally.
"""

import math
from collections import Counter
from dataclasses import dataclass

from .tokens import extract_unique_tokens, strip_markdown


@dataclass(frozen=True)
class TokenLevelMetrics:
    """Immutable result of a token-level evaluation (set-based)."""

    extracted_count: int
    sample_count: int
    intersection_count: int
    precision: float
    recall: float
    f1: float


def calculate_token_level_metrics(parsed_text: str, gold_text: str) -> TokenLevelMetrics:
    """Compute precision, recall, and F1 between parsed and gold text.

    Strips markdown from parsed_text before tokenization.
    Returns zero for all scores if either text is empty.
    """
    extracted_tokens = extract_unique_tokens(strip_markdown(parsed_text))
    sample_tokens = extract_unique_tokens(gold_text)

    intersection_count = len(extracted_tokens & sample_tokens)
    extracted_count = len(extracted_tokens)
    sample_count = len(sample_tokens)

    precision = intersection_count / extracted_count if extracted_count else 0.0
    recall = intersection_count / sample_count if sample_count else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return TokenLevelMetrics(
        extracted_count=extracted_count,
        sample_count=sample_count,
        intersection_count=intersection_count,
        precision=precision,
        recall=recall,
        f1=f1,
    )


def calculate_cosine_similarity(parsed_text: str, gold_text: str) -> float:
    """Compute cosine similarity between parsed and gold text using token frequency vectors.

    Strips markdown from parsed_text before comparison.
    Unlike precision/recall (which use sets), this accounts for how often each
    token appears — two texts with the same words but very different frequencies
    will score lower.

    Formula: cos(θ) = (A·B) / (|A| · |B|)

    Returns 0.0 if either text is empty.
    """
    freq_a = Counter(strip_markdown(parsed_text).split())
    freq_b = Counter(gold_text.split())

    if not freq_a or not freq_b:
        return 0.0

    dot = sum(freq_a[t] * freq_b[t] for t in freq_a if t in freq_b)
    mag_a = math.sqrt(sum(v ** 2 for v in freq_a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in freq_b.values()))

    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0
