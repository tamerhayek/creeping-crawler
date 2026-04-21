# CLAUDE.md

## Project overview

Crawl4AI Evaluation Framework — a Python tool that evaluates content extraction quality from web pages. It crawls URLs with Crawl4AI, parses the resulting markdown with URL-specific parsers, and scores extraction quality against gold standard samples using precision, recall, and F1. It also exposes a FastAPI REST server for all evaluation operations.

## Tech stack

- Python 3.11
- Conda for environment management + pip for packages
- Click for CLI
- Crawl4AI 0.8.x + Playwright for web crawling
- FastAPI + Uvicorn for the REST API
- Pytest for testing

## Setup

```bash
# Backend
cd backend
conda create -n crawl4ai-backend python=3.11 -y
conda activate crawl4ai-backend
pip install -r requirements.txt
python -m playwright install --with-deps chromium

# Frontend
cd frontend
conda create -n crawl4ai-frontend python=3.11 -y
conda activate crawl4ai-frontend
pip install -r requirements.txt
```

## Running

With Docker Compose (recommended):
```bash
docker compose up --build
```

Without Docker:
```bash
# Terminal 1 — backend API (port 8003)
conda activate crawl4ai-backend && python main.py serve

# Terminal 2 — frontend UI (port 8004)
conda activate crawl4ai-frontend && python app.py
```

Backend CLI commands:
```bash
cd backend
python main.py list-urls              # List evaluable URLs
python main.py run --url <URL>        # Evaluate a specific URL
python main.py serve                  # Start REST API server (default: 127.0.0.1:8003)
python main.py serve --host 0.0.0.0 --port 8080
```

## Testing

```bash
conda activate crawl4ai-backend
cd backend
pytest        # Run all tests
pytest -v     # Verbose
```

## Project structure

```
backend/              — Backend (Python, FastAPI, Crawl4AI)
  main.py             — CLI entry point (Click commands: list-urls, run, serve)
  requirements.txt    — Backend dependencies
  crawl_eval/         — Main package
    api.py            — FastAPI app creation + router registration
    schemas.py        — Pydantic request/response models
    services.py       — Shared business logic (domain validation, token eval, etc.)
    routes/           — API endpoint modules (one per domain)
      parse.py        — /parse endpoint
      domains.py      — /domains endpoint
      gold.py         — /gold_standard, /full_gold_standard, /gs_urls, /gold_text
      evaluate.py     — /evaluate, /full_gs_eval
    pipeline.py       — Orchestrates crawl → parse → evaluate
    crawler.py        — Fetches page content via Crawl4AI; returns PageContent (title, html_text)
    urls.py           — URL/domain management from gold samples
    tokens.py         — Whitespace-based tokenization + markdown stripping
    metrics.py        — Precision/recall/F1 calculation
    gold.py           — Gold standard sample loading
    parsers/          — Content parsers
      base.py         — ContentParser ABC
      registry.py     — URL-based parser selection
      default.py      — PassThroughParser (no-op)
      wikipedia.py    — WikipediaParser with section profiles
  gs/                 — Gold standard text samples (ground truth)
  tests/              — Pytest test suite
frontend/             — Frontend (Flask + Jinja2, port 8004)
  app.py              — Flask app (proxies to backend API)
  requirements.txt    — Frontend dependencies (flask, requests)
  templates/
    base.html.jinja   — Bootstrap 5 base layout
    index.html.jinja  — URL input form + GS dropdown
    result.html.jinja — Raw / Parsed / Gold Standard comparison + metrics
  static/
    style.css         — Text panel styles
```

## REST API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/parse?url=` | Crawl + parse a URL, return title/html_text/parsed_text |
| GET | `/domains` | List supported domains |
| GET | `/gold_standard?url=` | Gold standard entry for a URL |
| GET | `/full_gold_standard?domain=` | All GS entries for a domain |
| POST | `/evaluate` | Compute metrics given `{parsed_text, gold_text}` |
| GET | `/gs_urls` | List all gold standard URLs |
| GET | `/gold_text?url=` | Gold standard text for a URL (no crawl) |
| GET | `/full_gs_eval?domain=` | Averaged evaluation across all GS entries for a domain |

Errors: `400` unsupported domain, `404` URL not in GS, `503` unreachable URL.

## Key patterns

- **Async pipeline**: `crawl_and_evaluate()` is async; CLI wraps with `asyncio.run()`; API uses FastAPI's native async
- **Parser registry**: `get_parser_for_url()` selects parser by URL hostname; add new parsers there
- **Supported domain**: a domain is "supported" if it has entries in the `gs/` directory
- **URL ↔ filename mapping**: `https://en.wikipedia.org/wiki/X` → `en.wikipedia.org_wiki_X.txt`
- **Markdown stripping**: `strip_markdown()` in `tokens.py` removes markdown syntax before evaluation
- **Page profiles**: WikipediaParser uses per-page `WikipediaSectionProfile` configs in `PAGE_PROFILES`
- **Frozen dataclasses**: `TokenMetrics`, `EvaluationResult`, `WikipediaSectionProfile`
