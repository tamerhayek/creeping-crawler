"""Route for the comparison page (GET /compare)."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..client import evaluate, get_gold_text, get_gs_urls, parse_url
from ..templates import templates

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

    gs_urls = get_gs_urls()
    data, error = parse_url(url)

    if not error and url in gs_urls:
        gold_text = get_gold_text(url)
        if gold_text:
            data["gold_text"] = gold_text
            metrics = evaluate(data["parsed_text"], gold_text)
            if metrics:
                data["metrics"] = metrics

    return templates.TemplateResponse(
        request=request,
        name="result.html.jinja",
        context={"url": url, "data": data, "error": error, "gs_urls": gs_urls},
    )
