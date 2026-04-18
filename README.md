# Crawl4AI Evaluation Framework

A tool for evaluating content extraction quality from web pages. It crawls URLs using [Crawl4AI](https://github.com/unclecode/crawl4ai), parses the resulting markdown with URL-specific parsers, and measures extraction quality against gold standard samples using precision, recall, and F1 score.

## How it works

1. **Crawl** a URL and convert it to markdown using Crawl4AI + Playwright
2. **Parse** the markdown with a URL-specific parser (e.g., `WikipediaParser` for Wikipedia pages)
3. **Tokenize** both the extracted content and a gold standard sample
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
```

Example output:

```
URL: https://en.wikipedia.org/wiki/BabelNet
Parser: WikipediaParser
Gold sample: gs/en.wikipedia.org_wiki_BabelNet.txt
Extracted tokens: 1200
Sample tokens: 1150
Intersection: 1100
Recall: 0.9167
Precision: 0.9565
F1: 0.9362
```

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

1. Create a text file in `gs/` named as `domain_path.txt` (e.g., `en.wikipedia.org_wiki_PageName.txt`)
2. The file should contain the expected clean text content for that URL
3. The URL will automatically appear in `list-urls`

## Testing

```bash
pytest
```

## Project structure

```
main.py                    # CLI entry point
crawl_eval/                # Main package
  pipeline.py              # Crawl -> parse -> evaluate orchestration
  crawler.py               # Crawl4AI markdown fetching
  urls.py                  # URL management
  tokens.py                # Tokenization
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
