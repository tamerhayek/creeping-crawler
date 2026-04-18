from pydantic import BaseModel


class ParseResponse(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    parsed_text: str


class DomainsResponse(BaseModel):
    domains: list[str]


class GoldStandardEntry(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    gold_text: str


class GoldStandardResponse(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    gold_text: str


class FullGoldStandardResponse(BaseModel):
    gold_standard: list[GoldStandardEntry]


class EvaluateRequest(BaseModel):
    parsed_text: str
    gold_text: str


class TokenLevelEval(BaseModel):
    precision: float
    recall: float
    f1: float


class EvaluateResponse(BaseModel):
    token_level_eval: TokenLevelEval
    x_eval: dict = {}


class GsUrlsResponse(BaseModel):
    urls: list[str]


class GoldTextResponse(BaseModel):
    url: str
    gold_text: str
