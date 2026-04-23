"""Route for the comparison page (GET /compare)."""

import re

import mistune
from bs4 import BeautifulSoup
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..client import BackendUnavailable, evaluate, get_gold_text, get_gs_urls, parse_url
from ..templates import templates


def strip_markdown(text: str) -> str:
    """Convert markdown to plain text using mistune + BeautifulSoup."""
    html = mistune.html(text)
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(True):
        tag.unwrap()
    text = re.sub(r'[ \t]+', ' ', str(soup))
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

router = APIRouter()


@router.get("/compare", response_class=HTMLResponse)
def compare(request: Request, url: str = ""):
    """Parse a URL and render the results page.

    If the URL is in the gold standard, also fetches the gold text and
    computes evaluation metrics to show alongside the parsed output.

    Redirects to / if no URL is provided.
    """
    url = url.strip()
    if not url:
        return RedirectResponse(url="/")

    try:
        gs_urls = get_gs_urls()
        data, error = parse_url(url)

        if not error:
            data["cleaned_text"] = strip_markdown(data.get("parsed_text", ""))

        if not error and url in gs_urls:
            gold_text = get_gold_text(url)
            if gold_text:
                data["gold_text"] = gold_text
                metrics = evaluate(data["cleaned_text"], gold_text)
                if metrics:
                    data["metrics"] = metrics
    except BackendUnavailable:
        return templates.TemplateResponse(request=request, name="error.html.jinja", status_code=503)

    return templates.TemplateResponse(
        request=request,
        name="result.html.jinja",
        context={"url": url, "data": data, "error": error, "gs_urls": gs_urls},
    )
