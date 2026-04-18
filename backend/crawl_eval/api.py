import asyncio
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from .crawler import fetch_page
from .gold import gold_sample_path_for_url, load_sample_text
from .metrics import calculate_metrics
from .parsers import get_parser_for_url
from .tokens import extract_unique_tokens, strip_markdown
from .urls import get_available_urls, get_domains, get_urls_for_domain, is_supported_domain

app = FastAPI(title="Crawl4AI Evaluation API")


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ParseResponse(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    parsed_text: str


class DomainsResponse(BaseModel):
    domains: list[str]


class GoldStandardEntry(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    gold_text: str


class GoldStandardResponse(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    gold_text: str


class FullGoldStandardResponse(BaseModel):
    gold_standard: list[GoldStandardEntry]


class EvaluateRequest(BaseModel):
    parsed_text: str
    gold_text: str


class TokenLevelEval(BaseModel):
    precision: float
    recall: float
    f1: float


class EvaluateResponse(BaseModel):
    token_level_eval: TokenLevelEval
    x_eval: dict = {}


class GsUrlsResponse(BaseModel):
    urls: list[str]


class GoldTextResponse(BaseModel):
    url: str
    gold_text: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _domain_of(url: str) -> str:
    return urlparse(url).netloc


def _assert_supported_domain(domain: str) -> None:
    if not is_supported_domain(domain):
        raise HTTPException(status_code=400, detail=f"Unsupported domain: {domain}")


def _compute_token_eval(parsed_text: str, gold_text: str) -> TokenLevelEval:
    extracted_tokens = extract_unique_tokens(strip_markdown(parsed_text))
    sample_tokens = extract_unique_tokens(gold_text)
    metrics = calculate_metrics(extracted_tokens, sample_tokens)
    return TokenLevelEval(
        precision=metrics.precision,
        recall=metrics.recall,
        f1=metrics.f1,
    )


async def _build_gold_entry(url: str) -> GoldStandardEntry:
    domain = _domain_of(url)
    sample_path = gold_sample_path_for_url(url)
    gold_text = load_sample_text(sample_path)

    try:
        page = await fetch_page(url)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return GoldStandardEntry(
        url=url,
        domain=domain,
        title=page.title,
        html_text=page.html_text,
        gold_text=gold_text,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/parse", response_model=ParseResponse)
async def parse(url: str = Query(...)):
    domain = _domain_of(url)
    _assert_supported_domain(domain)

    try:
        page = await fetch_page(url)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    parser = get_parser_for_url(url)
    parsed_text = parser.parse(url, page.html_text)

    return ParseResponse(
        url=url,
        domain=domain,
        title=page.title,
        html_text=page.html_text,
        parsed_text=parsed_text,
    )


@app.get("/domains", response_model=DomainsResponse)
def domains():
    return DomainsResponse(domains=get_domains())


@app.get("/gold_standard", response_model=GoldStandardResponse)
async def gold_standard(url: str = Query(...)):
    domain = _domain_of(url)
    _assert_supported_domain(domain)

    sample_path = gold_sample_path_for_url(url)
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail=f"URL not found in gold standard: {url}")

    try:
        page = await fetch_page(url)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    gold_text = load_sample_text(sample_path)
    return GoldStandardResponse(
        url=url,
        domain=domain,
        title=page.title,
        html_text=page.html_text,
        gold_text=gold_text,
    )


@app.get("/full_gold_standard", response_model=FullGoldStandardResponse)
async def full_gold_standard(domain: str = Query(...)):
    _assert_supported_domain(domain)
    urls = get_urls_for_domain(domain)
    entries = await asyncio.gather(*[_build_gold_entry(url) for url in urls])
    return FullGoldStandardResponse(gold_standard=list(entries))


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(body: EvaluateRequest):
    token_eval = _compute_token_eval(body.parsed_text, body.gold_text)
    return EvaluateResponse(token_level_eval=token_eval)


@app.get("/gs_urls", response_model=GsUrlsResponse)
def gs_urls():
    return GsUrlsResponse(urls=get_available_urls())


@app.get("/gold_text", response_model=GoldTextResponse)
def gold_text(url: str = Query(...)):
    domain = _domain_of(url)
    _assert_supported_domain(domain)
    sample_path = gold_sample_path_for_url(url)
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail=f"URL not found in gold standard: {url}")
    return GoldTextResponse(url=url, gold_text=load_sample_text(sample_path))


@app.get("/full_gs_eval", response_model=EvaluateResponse)
async def full_gs_eval(domain: str = Query(...)):
    _assert_supported_domain(domain)
    urls = get_urls_for_domain(domain)

    async def _eval_url(url: str) -> TokenLevelEval:
        sample_path = gold_sample_path_for_url(url)
        gold_text = load_sample_text(sample_path)
        try:
            page = await fetch_page(url)
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
        parser = get_parser_for_url(url)
        parsed_text = parser.parse(url, page.html_text)
        return _compute_token_eval(parsed_text, gold_text)

    evals = await asyncio.gather(*[_eval_url(url) for url in urls])
    n = len(evals)
    avg_precision = sum(e.precision for e in evals) / n
    avg_recall = sum(e.recall for e in evals) / n
    avg_f1 = sum(e.f1 for e in evals) / n

    return EvaluateResponse(
        token_level_eval=TokenLevelEval(
            precision=avg_precision,
            recall=avg_recall,
            f1=avg_f1,
        )
    )
