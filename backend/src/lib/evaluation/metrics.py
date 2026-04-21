"""Token-level evaluation metrics: precision, recall, and F1.

All metrics operate on sets of tokens, treating each unique token as a binary label.

Definitions (per project spec):
    precision = |extracted ∩ gold| / |extracted|  — fraction of extracted tokens that are correct
    recall    = |extracted ∩ gold| / |gold|        — fraction of gold tokens that were found
    f1        = 2 * precision * recall / (precision + recall)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenMetrics:
    """Immutable result of a token-level evaluation."""

    extracted_count: int     # number of unique tokens in the parser output
    sample_count: int        # number of unique tokens in the gold standard
    intersection_count: int  # tokens present in both sets
    precision: float
    recall: float
    f1: float


def calculate_metrics(extracted_tokens: set[str], sample_tokens: set[str]) -> TokenMetrics:
    """Compute precision, recall, and F1 between two token sets.

    Returns zero for all scores if either set is empty.
    """
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

    return TokenMetrics(
        extracted_count=extracted_count,
        sample_count=sample_count,
        intersection_count=intersection_count,
        precision=precision,
        recall=recall,
        f1=f1,
    )
