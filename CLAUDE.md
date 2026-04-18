# CLAUDE.md

## Project overview

Crawl4AI Evaluation Framework — a Python tool that evaluates content extraction quality from web pages. It crawls URLs with Crawl4AI, parses the resulting markdown with URL-specific parsers, and scores extraction quality against gold standard samples using precision, recall, and F1. It also exposes a FastAPI REST server for all evaluation operations.

## Tech stack

- Python 3.11 (>=3.11, <3.12)
- Pixi for environment/dependency management
- Click for CLI
- Crawl4AI 0.8.x + Playwright for web crawling
- FastAPI + Uvicorn for the REST API
- Pytest for testing

## Setup

```bash
pixi install
```

## Running

```bash
python main.py list-urls              # List evaluable URLs
python main.py run --url <URL>        # Evaluate a specific URL
python main.py serve                  # Start REST API server (default: 127.0.0.1:8003)
python main.py serve --host 0.0.0.0 --port 8080
```

## Testing

```bash
pytest                # Run all tests
pytest -v             # Verbose
```

## Project structure

- `main.py` — CLI entry point (Click commands: `list-urls`, `run`, `serve`)
- `crawl_eval/` — Main package
  - `api.py` — FastAPI REST API (6 endpoints)
  - `pipeline.py` — Orchestrates crawl → parse → evaluate
  - `crawler.py` — Fetches page content via Crawl4AI; returns `PageContent` (title, html_text)
  - `urls.py` — URL/domain management from gold samples
  - `tokens.py` — Whitespace-based tokenization + markdown stripping
  - `metrics.py` — Precision/recall/F1 calculation
  - `gold.py` — Gold standard sample loading
  - `parsers/` — Content parsers
    - `base.py` — `ContentParser` ABC
    - `registry.py` — URL-based parser selection
    - `default.py` — `PassThroughParser` (no-op)
    - `wikipedia.py` — `WikipediaParser` with section profiles
- `gs/` — Gold standard text samples (ground truth)
- `tests/` — Pytest test suite

## REST API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/parse?url=` | Crawl + parse a URL, return title/html_text/parsed_text |
| GET | `/domains` | List supported domains |
| GET | `/gold_standard?url=` | Gold standard entry for a URL |
| GET | `/full_gold_standard?domain=` | All GS entries for a domain |
| POST | `/evaluate` | Compute metrics given `{parsed_text, gold_text}` |
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
