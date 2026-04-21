"""Pydantic schemas for gold standard endpoints."""

from pydantic import BaseModel


class GoldStandardEntry(BaseModel):
    """A single gold standard entry: crawled content + manually curated gold text."""

    url: str
    domain: str
    title: str
    html_text: str   # raw markdown from the crawler — input to the parser
    gold_text: str   # manually curated clean text — ground truth for evaluation


class FullGoldStandardResponse(BaseModel):
    """Response for GET /full_gold_standard: all entries for a domain."""

    gold_standard: list[GoldStandardEntry]


class GsUrlsResponse(BaseModel):
    """Response for GET /gs_urls: list of all gold standard URLs."""

    urls: list[str]


class GoldTextResponse(BaseModel):
    """Response for GET /gold_text: gold text for a single URL."""

    url: str
    gold_text: str
