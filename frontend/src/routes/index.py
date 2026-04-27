"""Route for the home page (GET /)."""

from collections import defaultdict
from urllib.parse import urlparse

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..client import BackendUnavailable, get_gs_urls
from ..templates import templates

router = APIRouter()


def _group_by_domain(urls: list[str]) -> dict[str, list[str]]:
    """Group a list of URLs by their netloc, stripping leading 'www.'."""
    grouped: dict[str, list[str]] = defaultdict(list)
    for url in urls:
        netloc = urlparse(url).netloc.removeprefix("www.")
        grouped[netloc].append(url)
    return dict(grouped)


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Render the home page with the URL input form and GS dropdown."""
    try:
        gs_urls = get_gs_urls()
    except BackendUnavailable:
        return templates.TemplateResponse(request=request, name="error.html.jinja", status_code=503)
    return templates.TemplateResponse(
        request=request,
        name="index.html.jinja",
        context={"gs_urls": gs_urls, "gs_by_domain": _group_by_domain(gs_urls)},
    )
