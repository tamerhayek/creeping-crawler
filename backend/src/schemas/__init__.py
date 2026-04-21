from .domains import DomainsResponse
from .evaluate import EvaluateRequest, EvaluateResponse, TokenLevelEval
from .gold import FullGoldStandardResponse, GoldStandardEntry, GoldStandardResponse, GsUrlsResponse, GoldTextResponse
from .parse import ParseResponse

__all__ = [
    "DomainsResponse",
    "EvaluateRequest",
    "EvaluateResponse",
    "TokenLevelEval",
    "GoldStandardEntry",
    "GoldStandardResponse",
    "GsUrlsResponse",
    "GoldTextResponse",
    "FullGoldStandardResponse",
    "ParseResponse",
]
