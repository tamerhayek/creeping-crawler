"""Pydantic request/response schemas for the Crawl4AI Evaluation API."""

from .domains import DomainsResponse
from .evaluate import EvaluateRequest, EvaluateResponse, TokenLevelEval
from .gold import FullGoldStandardResponse, GoldStandardEntry, GoldTextResponse, GsUrlsResponse
from .parse import ParseResponse

__all__ = [
    "DomainsResponse",
    "EvaluateRequest",
    "EvaluateResponse",
    "TokenLevelEval",
    "GoldStandardEntry",
    "GoldTextResponse",
    "GsUrlsResponse",
    "FullGoldStandardResponse",
    "ParseResponse",
]
