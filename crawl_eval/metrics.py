from dataclasses import dataclass


@dataclass(frozen=True)
class TokenMetrics:
    extracted_count: int
    sample_count: int
    intersection_count: int
    recall: float
    precision: float
    f1: float


def calculate_metrics(extracted_tokens: set[str], sample_tokens: set[str]) -> TokenMetrics:
    intersection_count = len(extracted_tokens & sample_tokens)
    extracted_count = len(extracted_tokens)
    sample_count = len(sample_tokens)

    recall = intersection_count / extracted_count if extracted_count else 0.0
    precision = intersection_count / sample_count if sample_count else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return TokenMetrics(
        extracted_count=extracted_count,
        sample_count=sample_count,
        intersection_count=intersection_count,
        recall=recall,
        precision=precision,
        f1=f1,
    )
