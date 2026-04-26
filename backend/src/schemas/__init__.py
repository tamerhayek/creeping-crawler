"""Pydantic request/response schemas for the Crawl4AI Evaluation API."""

from .domains import DomainsResponse
from .evaluate import EvaluateRequest, EvaluateResponse, SimilarityEval, TokenLevelEval
from .gold import FullGoldStandardResponse, GoldStandardResponse, GoldTextResponse, GsUrlsResponse
from .parse import ParseRequest, ParseResponse

__all__ = [
    "DomainsResponse",
    "EvaluateRequest",
    "EvaluateResponse",
    "TokenLevelEval",
    "SimilarityEval",
    "GoldStandardResponse",
    "GoldTextResponse",
    "GsUrlsResponse",
    "FullGoldStandardResponse",
    "ParseRequest",
    "ParseResponse",
]
