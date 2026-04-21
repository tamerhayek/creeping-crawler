from pydantic import BaseModel

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