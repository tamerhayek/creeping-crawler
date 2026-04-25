"""Evaluation metrics for token-level and token-count-level comparison.

token_level_eval  — operates on token *sets* (presence/absence)
similarity_eval   — operates on token *frequency vectors* (cosine, jaccard, excess_ratio)

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


@dataclass(frozen=True)
class ContentMetrics:
    """Immutable result of frequency-vector-based content evaluation.

    cosine       — cos(θ) between frequency vectors; high → similar distribution.
    jaccard      — |A∩B| / |A∪B| on token sets; penalises both extra and missing tokens.
    excess_ratio — fraction of parsed tokens not matched by gold (lower is better).
                   Computed on frequency vectors: 1 - overlap/total_parsed, where
                   overlap = Σ min(freq_parsed[t], freq_gold[t]).
    """

    cosine: float
    jaccard: float
    excess_ratio: float


def calculate_token_level_metrics(parsed_text: str, gold_text: str) -> TokenLevelMetrics:
    """Compute precision, recall, and F1 between parsed and gold text.

    Both texts are passed through strip_markdown before tokenization so that
    unicode normalisation (quotes, dashes) and HTML-entity decoding are applied
    symmetrically. Returns zero for all scores if either text is empty.
    """
    extracted_tokens = extract_unique_tokens(strip_markdown(parsed_text))
    sample_tokens = extract_unique_tokens(strip_markdown(gold_text))

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


def calculate_content_metrics(parsed_text: str, gold_text: str) -> ContentMetrics:
    """Compute cosine similarity, Jaccard similarity, and excess ratio.

    All three metrics strip markdown before processing.

    cosine similarity — frequency-vector dot product normalised by magnitudes.
        cos(θ) = (A·B) / (|A|·|B|)
        Sensitive to token frequency distributions; less sensitive to extra content.

    jaccard similarity — set overlap normalised by union size.
        J = |A∩B| / |A∪B|
        Penalises both extra tokens (enlarges union) and missing tokens.

    excess ratio — fraction of parsed token occurrences not covered by gold.
        excess = 1 - Σ min(fp[t], fg[t]) / Σ fp[t]
        Directly measures how much extracted content is noise. Lower is better.

    Returns zeros for all metrics if either text is empty.
    """
    parsed_stripped = strip_markdown(parsed_text)
    gold_stripped = strip_markdown(gold_text)

    freq_p = Counter(parsed_stripped.split())
    freq_g = Counter(gold_stripped.split())

    if not freq_p or not freq_g:
        return ContentMetrics(cosine=0.0, jaccard=0.0, excess_ratio=0.0)

    # Cosine
    dot = sum(freq_p[t] * freq_g[t] for t in freq_p if t in freq_g)
    mag_p = math.sqrt(sum(v ** 2 for v in freq_p.values()))
    mag_g = math.sqrt(sum(v ** 2 for v in freq_g.values()))
    cosine = dot / (mag_p * mag_g) if mag_p and mag_g else 0.0

    # Jaccard (set-based)
    set_p = set(freq_p)
    set_g = set(freq_g)
    union = len(set_p | set_g)
    jaccard = len(set_p & set_g) / union if union else 0.0

    # Excess ratio (frequency-based)
    overlap = sum(min(freq_p[t], freq_g[t]) for t in freq_p if t in freq_g)
    total_parsed = sum(freq_p.values())
    excess_ratio = 1.0 - (overlap / total_parsed) if total_parsed else 0.0

    return ContentMetrics(cosine=cosine, jaccard=jaccard, excess_ratio=excess_ratio)
