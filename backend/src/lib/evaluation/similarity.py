"""Similarity evaluation (frequency-vector-based): cosine, Jaccard, excess ratio.

Operates on token *frequency vectors* (Counter), making it sensitive to
repeated terms and to the overall volume of extracted content relative to gold.
"""

import math
from collections import Counter
from dataclasses import dataclass

from .tokens import strip_markdown


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
