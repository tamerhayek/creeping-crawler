"""Pydantic schemas for gold standard endpoints."""

from pydantic import BaseModel


class GoldStandardResponse(BaseModel):
    """Response for GET /gold_standard: crawled content + manually curated gold text."""

    url: str
    domain: str
    title: str
    html_text: str   # raw HTML of the page
    gold_text: str   # manually curated clean text — ground truth for evaluation


class FullGoldStandardResponse(BaseModel):
    """Response for GET /full_gold_standard: all entries for a domain."""

    gold_standard: list[GoldStandardResponse]


class GoldStandardUrlsResponse(BaseModel):
    """Response for GET /gold_standard_urls: list of all gold standard URLs."""

    urls: list[str]
