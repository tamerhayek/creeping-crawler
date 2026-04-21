from pydantic import BaseModel

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

class GsUrlsResponse(BaseModel):
    urls: list[str]

class GoldTextResponse(BaseModel):
    url: str
    gold_text: str
