"""Parser & Evaluation page (GET /parser)."""

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse

from ..client import (
    BackendUnavailable,
    evaluate,
    evaluate_judge,
    get_domains,
    get_gold_standard,
    get_gs_urls,
    parse_url,
)
from ..templates import templates
from ..utils import strip_markdown

router = APIRouter()


@router.get("/parser", response_class=HTMLResponse)
def parser_eval(
    request: Request,
    url: str = Query(default=""),
    mode: str = Query(default="live"),
):
    """Parse a URL (live or local), evaluate against GS if available, return results."""
    try:
        domains = get_domains()
        # URLs grouped by domain, so the page can show two linked dropdowns
        # (pick a domain, then pick one of its URLs).
        gs_urls_by_domain = {domain: get_gs_urls(domain) for domain in domains}
        all_gs_urls = [
            gs_url
            for urls in gs_urls_by_domain.values()
            for gs_url in urls
        ]

        result = None
        if url.strip():
            local = mode == "local"
            data, error = parse_url(url.strip(), local=local)
            result = {"data": data, "error": error, "url": url.strip(), "mode": mode}

            if not error:
                # Strip markdown from parsed_text so the diff and the metrics
                # compare clean text (without #, *, links, etc.) against gold_text.
                result["cleaned_text"] = strip_markdown(data.get("parsed_text", ""))

                # If the URL is in the gold standard, fetch the gold text and
                # compute both quantitative and judge evaluations.
                if url.strip() in all_gs_urls:
                    gold_entry = get_gold_standard(url.strip())
                    if gold_entry:
                        result["gold_text"] = gold_entry["gold_text"]
                        result["eval"] = evaluate(result["cleaned_text"], gold_entry["gold_text"])
                        result["judge"] = evaluate_judge(result["cleaned_text"], gold_entry["gold_text"])
    except BackendUnavailable:
        return templates.TemplateResponse(
            request=request, name="error.html.jinja", status_code=503
        )

    return templates.TemplateResponse(
        request=request,
        name="parser_eval.html.jinja",
        context={
            "gs_urls_by_domain": gs_urls_by_domain,
            "result": result,
            "selected_url": url.strip(),
            "selected_mode": mode,
        },
    )
