"""Route for the comparison page (GET /compare)."""

from bs4 import BeautifulSoup
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..client import BackendUnavailable, evaluate, get_gold_text, get_gs_urls, parse_url
from ..templates import templates
from ..utils import _QUOTE_TABLE, strip_markdown

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
