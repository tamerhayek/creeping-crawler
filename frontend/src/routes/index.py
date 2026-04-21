"""Route for the home page (GET /)."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..client import get_gs_urls
from ..templates import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Render the home page with the URL input form and GS dropdown."""
    return templates.TemplateResponse(
        request=request,
        name="index.html.jinja",
        context={"gs_urls": get_gs_urls()},
    )
