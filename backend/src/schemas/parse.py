"""Pydantic schemas for the parse endpoint."""

from pydantic import BaseModel


class ParseResponse(BaseModel):
    """Response for GET /parse: crawled content and parser output."""

    url: str
    domain: str
    title: str
    html_text: str    # raw markdown from the crawler
    parsed_text: str  # clean text produced by the domain-specific parser
