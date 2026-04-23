"""Pydantic schemas for the parse endpoint."""

from pydantic import BaseModel


class ParseRequest(BaseModel):
    """Request body for POST /parse."""

    url: str
    html_text: str


class ParseResponse(BaseModel):
    """Response for GET /parse and POST /parse."""

    url: str
    domain: str
    title: str
    html_text: str    # raw markdown from the crawler
    parsed_text: str  # clean text produced by the domain-specific parser
