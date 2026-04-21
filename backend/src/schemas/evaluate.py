"""Pydantic schemas for evaluation endpoints."""

from pydantic import BaseModel


class EvaluateRequest(BaseModel):
    """Request body for POST /evaluate."""

    parsed_text: str  # output of the parser
    gold_text: str    # manually curated ground truth


class TokenLevelEval(BaseModel):
    """Token-level precision, recall, and F1 scores."""

    precision: float
    recall: float
    f1: float


class EvaluateResponse(BaseModel):
    """Response for POST /evaluate and GET /full_gs_eval."""

    token_level_eval: TokenLevelEval
    x_eval: dict = {}  # reserved for additional evaluation methods
