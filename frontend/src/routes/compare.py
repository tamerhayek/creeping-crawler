from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..client import evaluate, get_gold_text, get_gs_urls, parse_url

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/compare", response_class=HTMLResponse)
def compare(request: Request, url: str = ""):
    url = url.strip()
    if not url:
        return RedirectResponse(url="/")

    gs_urls = get_gs_urls()
    data: dict = {}
    error: str | None = None

    data, error = parse_url(url)

    if not error and url in gs_urls:
        gold_text = get_gold_text(url)
        if gold_text:
            data["gold_text"] = gold_text
            metrics = evaluate(data["parsed_text"], gold_text)
            if metrics:
                data["metrics"] = metrics

    return templates.TemplateResponse(
        "result.html.jinja",
        {"request": request, "url": url, "data": data, "error": error, "gs_urls": gs_urls},
    )
