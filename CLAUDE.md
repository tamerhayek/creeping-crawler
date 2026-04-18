# CLAUDE.md

## Project overview

Crawl4AI Evaluation Framework — a Python tool that evaluates content extraction quality from web pages. It crawls URLs with Crawl4AI, parses the resulting markdown with URL-specific parsers, and scores extraction quality against gold standard samples using precision, recall, and F1.

## Tech stack

- Python 3.11 (>=3.11, <3.12)
- Pixi for environment/dependency management
- Click for CLI
- Crawl4AI + Playwright for web crawling
- Pytest for testing

## Setup

```bash
pixi install
```

## Running

```bash
python main.py list-urls              # List evaluable URLs
python main.py run --url <URL>        # Evaluate a specific URL
```

## Testing

```bash
pytest                # Run all tests
pytest -v             # Verbose
```

## Project structure

- `main.py` — CLI entry point (Click commands)
- `crawl_eval/` — Main package
  - `pipeline.py` — Orchestrates crawl → parse → evaluate
  - `crawler.py` — Fetches markdown via Crawl4AI
  - `urls.py` — URL management from gold samples
  - `tokens.py` — Whitespace-based tokenization
  - `metrics.py` — Precision/recall/F1 calculation
  - `gold.py` — Gold standard sample loading
  - `parsers/` — Content parsers
    - `base.py` — `ContentParser` ABC
    - `registry.py` — URL-based parser selection
    - `default.py` — `PassThroughParser` (no-op)
    - `wikipedia.py` — `WikipediaParser` with section profiles
- `gs/` — Gold standard text samples (ground truth)
- `tests/` — Pytest test suite

## Key patterns

- **Async pipeline**: `crawl_and_evaluate()` is async; CLI wraps with `asyncio.run()`
- **Parser registry**: `get_parser_for_url()` selects parser by URL hostname; add new parsers there
- **URL ↔ filename mapping**: `https://en.wikipedia.org/wiki/X` → `en.wikipedia.org_wiki_X.txt`
- **Page profiles**: WikipediaParser uses per-page `WikipediaSectionProfile` configs in `PAGE_PROFILES`
- **Frozen dataclasses**: `TokenMetrics`, `EvaluationResult`, `WikipediaSectionProfile`
