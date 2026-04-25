"""Pydantic schemas for evaluation endpoints."""

from pydantic import BaseModel


class EvaluateRequest(BaseModel):
    parsed_text: str
    gold_text: str


class TokenLevelEval(BaseModel):
    precision: float
    recall: float
    f1: float


class SimilarityEval(BaseModel):
    cosine: float
    jaccard: float
    excess_ratio: float


class EvaluateResponse(BaseModel):
    token_level_eval: TokenLevelEval
    similarity_eval: SimilarityEval
