# Crawl4AI Evaluation Framework

A tool for evaluating content extraction quality from web pages. It crawls URLs using [Crawl4AI](https://github.com/unclecode/crawl4ai), parses the resulting markdown with URL-specific parsers, and measures extraction quality against gold standard samples using precision, recall, and F1 score. A FastAPI REST server exposes all functionality over HTTP.

## How it works

1. **Crawl** a URL and convert it to markdown using Crawl4AI + Playwright
2. **Parse** the markdown with a URL-specific parser (e.g., `WikipediaParser` for Wikipedia pages)
3. **Tokenize** both the extracted content and a gold standard sample (stripping markdown before comparison)
4. **Evaluate** by computing token-level precision, recall, and F1

## Setup

Requires [Pixi](https://pixi.sh) for environment management.

```bash
pixi install
```

## Usage

### CLI

```bash
# List all available URLs for evaluation
python main.py list-urls

# Run evaluation on a specific URL
python main.py run --url https://en.wikipedia.org/wiki/BabelNet

# Start the REST API server
python main.py serve                          # 127.0.0.1:8003
python main.py serve --host 0.0.0.0 --port 8080
```

### REST API

Once the server is running, the following endpoints are available:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/parse?url=` | Crawl and parse a URL |
| GET | `/domains` | List supported domains |
| GET | `/gold_standard?url=` | Gold standard entry for a URL |
| GET | `/full_gold_standard?domain=` | All GS entries for a domain |
| POST | `/evaluate` | Compute metrics from parsed + gold text |
| GET | `/full_gs_eval?domain=` | Averaged evaluation over a full domain GS |

Interactive docs available at `http://127.0.0.1:8003/docs`.

**Example — parse a URL:**
```
GET /parse?url=https://en.wikipedia.org/wiki/BabelNet
```
```json
{
  "url": "https://en.wikipedia.org/wiki/BabelNet",
  "domain": "en.wikipedia.org",
  "title": "BabelNet - Wikipedia",
  "html_text": "...",
  "parsed_text": "..."
}
```

**Example — evaluate:**
```
POST /evaluate
{"parsed_text": "...", "gold_text": "..."}
```
```json
{
  "token_level_eval": {"precision": 0.87, "recall": 0.91, "f1": 0.89},
  "x_eval": {}
}
```

**Error codes:** `400` unsupported domain · `404` URL not in gold standard · `503` URL unreachable

### Python API

```python
import asyncio
from crawl_eval.pipeline import crawl_and_evaluate

result = asyncio.run(crawl_and_evaluate(url="https://en.wikipedia.org/wiki/Minerva"))
print(f"F1: {result.metrics.f1:.4f}")
```

## Adding a new parser

1. Create a class extending `ContentParser` in `crawl_eval/parsers/`
2. Implement the `parse(url, markdown) -> str` method
3. Register it in `crawl_eval/parsers/registry.py` by mapping hostnames to your parser

## Adding a new gold standard sample

1. Create a text file in `gs/` named `domain_path.txt` (e.g., `en.wikipedia.org_wiki_PageName.txt`)
2. The file should contain the expected clean text content for that URL
3. The URL will automatically appear in `list-urls` and `/domains`

## Testing

```bash
pytest
```

## Project structure

```
main.py                    # CLI entry point (list-urls, run, serve)
crawl_eval/                # Main package
  api.py                   # FastAPI REST API
  pipeline.py              # Crawl -> parse -> evaluate orchestration
  crawler.py               # Crawl4AI page fetching (title + markdown)
  urls.py                  # URL and domain management
  tokens.py                # Tokenization + markdown stripping
  metrics.py               # Precision / recall / F1
  gold.py                  # Gold standard loading
  parsers/
    base.py                # ContentParser ABC
    registry.py            # URL -> parser mapping
    default.py             # PassThroughParser
    wikipedia.py           # WikipediaParser
gs/                        # Gold standard samples
tests/                     # Test suite
```
