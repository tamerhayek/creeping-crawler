# CLAUDE.md

## Project overview

Crawl4AI Evaluation Framework — a Python tool that evaluates content extraction quality from web pages. It crawls URLs with Crawl4AI, parses the resulting markdown with URL-specific parsers, and scores extraction quality against gold standard samples using precision, recall, and F1. It also exposes a FastAPI REST server for all evaluation operations.

## Tech stack

- Python 3.11
- Conda for environment management + pip for packages
- Crawl4AI + Playwright for web crawling
- FastAPI + Uvicorn for the REST API (both backend and frontend)
- Pytest for testing

## Setup

```bash
make envs       # Create both conda environments and install dependencies
```

Or manually:

```bash
# Backend
make env-backend

# Frontend
make env-frontend
```

## Running

With Docker Compose (recommended):
```bash
docker compose up --build
```

Without Docker (two terminals):
```bash
make run-backend    # Backend API on port 8003
make run-frontend   # Frontend UI on port 8004
```

## Testing

```bash
conda activate crawl4ai-backend
cd backend
pytest        # Run all tests
pytest -v     # Verbose
```

## Makefile commands

| Command | Description |
|---------|-------------|
| `make envs` | Create both conda environments |
| `make env-backend` | Create backend conda env |
| `make env-frontend` | Create frontend conda env |
| `make run-backend` | Start backend API (port 8003) |
| `make run-frontend` | Start frontend UI (port 8004) |
| `make crawl` | Crawl all GS URLs, save results to `gs_results/` |
| `make crawl -- --domain <domain>` | Crawl only the given domain |
| `make crawl -- --update-json` | Crawl and update `html_text` in `gs_data/` JSON files |
| `make freeze` | Update both requirements.txt from pip freeze |
| `make freeze-backend` | Update backend/requirements.txt |
| `make freeze-frontend` | Update frontend/requirements.txt |
| `make delete-envs` | Remove both conda environments |

## Project structure

```
backend/                      — Backend (Python, FastAPI, Crawl4AI)
  crawl_gs.py                 — Crawl GS URLs; save results to gs_results/ (--update-json to also update gs_data/)
  src/
    server.py                 — FastAPI app entry point (uvicorn src.server:app)
    routes/                   — API endpoint modules
      parse.py                — /parse endpoint
      domains.py              — /domains endpoint
      gold.py                 — /gold_standard, /full_gold_standard, /gs_urls, /gold_text
      evaluate.py             — /evaluate, /full_gs_eval
    schemas/                  — Pydantic request/response models (per domain)
      parse.py
      domains.py
      gold.py
      evaluate.py
    lib/                      — Core business logic
      services.py             — Shared logic (domain validation, token eval, fetch_page_for_url, etc.)
      crawling/
        crawler.py            — Fetches page content via Crawl4AI; returns PageContent
        configs/              — Per-domain CrawlerRunConfig definitions
      evaluation/
        metrics.py            — Precision/recall/F1 calculation
        tokens.py             — Whitespace-based tokenization + markdown stripping
      gold_standard/
        gold.py               — Gold standard sample loading
        urls.py               — URL/domain management from gold samples
      parsers/
        base.py               — ContentParser ABC
        registry.py           — URL-based parser selection
        default.py            — PassThroughParser (no-op)
        wikipedia.py          — WikipediaParser with section profiles
        cnbc.py               — CNBCParser
        espn.py               — ESPNParser
  tests/                      — Pytest test suite
  requirements.txt            — Backend dependencies
frontend/                     — Frontend (FastAPI + Jinja2, port 8004)
  src/
    app.py                    — FastAPI app entry point (uvicorn src.app:app)
    client.py                 — HTTP client to backend API
    templates.py              — Jinja2 template rendering helpers
    routes/
      index.py                — URL input form + GS dropdown
      compare.py              — Raw / Parsed / Gold Standard comparison + metrics
  templates/
    base.html.jinja           — Bootstrap 5 base layout
    index.html.jinja          — URL input form
    result.html.jinja         — Comparison view + metrics
  static/
    style.css                 — Text panel styles
  requirements.txt            — Frontend dependencies
gs_data/                      — Gold standard data (JSON files per domain)
  it_wikipedia_org_gs.json
  www.espn_gs.json
  www_cnbc_com_gs.json
  www_xe_com_gs.json
gs_results/                   — crawl_gs.py output (gitignored); html/, cleaned_html/, markdown/
domains.json                  — Supported domain registry
Makefile                      — Dev commands
docker-compose.yml            — Docker Compose config
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

- **Parser registry**: `get_parser_for_url()` in `src/lib/parsers/registry.py` selects parser by URL hostname; add new parsers there
- **Supported domain**: a domain is "supported" if it has entries in `gs_data/`
- **Gold standard format**: JSON files named `<domain>_gs.json` in `gs_data/`; each entry has `url`, `domain`, `title`, `html_text`, `gold_text`
- **Fetch strategy**: always use `fetch_page_for_url()` in `src/lib/services.py` — it uses the stored `html_text` snapshot from `gs_data/` when available, falling back to a live crawl if the snapshot produces empty markdown
- **HTML-to-markdown config**: `fetch_page_from_html()` uses a browser-free `CrawlerRunConfig` (no `magic`) so Crawl4AI skips Playwright and runs only the HTML→markdown pipeline; domain extraction filters are preserved
- **Markdown stripping**: `strip_markdown()` in `src/lib/evaluation/tokens.py` removes markdown before scoring
- **Page profiles**: WikipediaParser uses per-page `WikipediaSectionProfile` configs in `PAGE_PROFILES`
- **Frozen dataclasses**: `TokenMetrics`, `EvaluationResult`, `WikipediaSectionProfile`
