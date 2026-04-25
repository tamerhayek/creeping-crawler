"""Route for the comparison page (GET /compare)."""

import html as html_mod
import re

import mistune
from bs4 import BeautifulSoup
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..client import BackendUnavailable, evaluate, get_gold_text, get_gs_urls, parse_url
from ..templates import templates


_QUOTE_TABLE = str.maketrans({
    '\u2018': "'",   # left single quotation mark
    '\u2019': "'",   # right single quotation mark / apostrophe
    '\u201c': '"',   # left double quotation mark
    '\u201d': '"',   # right double quotation mark
    '\u2013': '-',   # en dash
    '\u2014': '-',   # em dash
})


def strip_markdown(text: str) -> str:
    """Convert markdown to plain text using mistune + BeautifulSoup.

    Normalises unicode typographic quotes and dashes to ASCII equivalents
    so the diff view is not polluted by quote-style differences.
    """
    text = text.translate(_QUOTE_TABLE)
    html = mistune.html(text)
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(True):
        tag.unwrap()
    text = re.sub(r'[ \t]+', ' ', str(soup))
    text = re.sub(r'\n+', '\n', text)
    text = html_mod.unescape(text)
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
            raw_html = data.get("html_text", "")
            if raw_html:
                data["html_text"] = BeautifulSoup(raw_html, "html.parser").prettify()

        if not error and url in gs_urls:
            gold_text = get_gold_text(url)
            if gold_text:
                data["gold_text"] = gold_text.translate(_QUOTE_TABLE)
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
