"""Pydantic request/response schemas for the Crawl4AI Evaluation API."""

from .domains import DomainsResponse
from .evaluate import EvaluateRequest, EvaluateResponse, SimilarityEval, TokenLevelEval
from .gold import FullGoldStandardResponse, GoldStandardEntry, GoldTextResponse, GsUrlsResponse
from .parse import ParseRequest, ParseResponse

__all__ = [
    "DomainsResponse",
    "EvaluateRequest",
    "EvaluateResponse",
    "TokenLevelEval",
    "SimilarityEval",
    "GoldStandardEntry",
    "GoldTextResponse",
    "GsUrlsResponse",
    "FullGoldStandardResponse",
    "ParseRequest",
    "ParseResponse",
]
