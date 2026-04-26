# Crawl4AI Evaluation Framework

A Python tool that evaluates content extraction quality from web pages. It crawls URLs with Crawl4AI, parses the resulting markdown with URL-specific parsers, and scores extraction quality against gold standard samples using two evaluation groups: token-level (precision/recall/F1) and similarity (cosine/jaccard/excess ratio).

## Requirements

- [Conda](https://docs.conda.io/en/latest/)
- Python 3.11

## Setup

```bash
make envs
```

This creates two conda environments (`crawl4ai-backend` and `crawl4ai-frontend`) and installs all dependencies.

## Running

**With Docker Compose (recommended):**
```bash
docker compose up --build
```

**Without Docker (two terminals):**
```bash
make run-backend    # http://localhost:8003
make run-frontend   # http://localhost:8004
```

## Development

```bash
make freeze         # Snapshot requirements.txt files from current envs
make delete-envs    # Remove conda environments
```

### Crawling gold standard URLs

Results are saved to `gs_results/`:

| Directory | Content |
|-----------|---------|
| `html/` | Raw HTML, prettified |
| `cleaned_html/` | Cleaned HTML, prettified |
| `markdown/` | Raw markdown from Crawl4AI (`.md`) |
| `stripped/` | Plain text after markdown stripping (`.txt`) |
| `parsed/` | Domain-specific parser output (`.txt`) |

The `stripped/` and `parsed/` outputs mirror the real application pipeline: `strip_markdown()` removes markdown syntax, then the domain parser (e.g. `WikipediaParser`, `CnbcParser`) applies its own extraction logic. The parser used is logged for each URL.

```bash
make crawl                                        # all domains
make crawl -- --domain www.xe.com                 # single domain
make crawl -- --update-json                       # all domains + update html_text in gs_data/
make crawl -- --domain www.xe.com --update-json   # single domain + update JSON
```

## Project Structure

```
backend/src/
├── server.py                 # FastAPI app entry point
├── routes/                   # API route handlers
│   ├── domains.py
│   ├── parse.py
│   ├── evaluate.py
│   └── gold.py
├── schemas/                  # Pydantic request/response models
│   ├── domains.py            # DomainsResponse
│   ├── parse.py              # ParseRequest, ParseResponse
│   ├── evaluate.py           # EvaluateRequest, EvaluateResponse, TokenLevelEval, SimilarityEval
│   └── gold.py               # GoldStandardResponse, FullGoldStandardResponse, GsUrlsResponse, GoldTextResponse
└── lib/                      # Core library (no FastAPI dependencies except utils)
    ├── utils.py              # domain_of, assert_supported_domain
    ├── crawling/
    │   ├── crawler.py        # fetch_page, fetch_page_from_html, fetch_page_for_url
    │   └── domains/          # Domain-specific CrawlerRunConfig
    │       ├── registry.py
    │       ├── wikipedia.py
    │       ├── espn.py
    │       ├── cnbc.py
    │       └── xe.py
    ├── parsers/
    │   ├── base.py           # ContentParser abstract class
    │   ├── default.py        # PassThroughParser (fallback)
    │   ├── registry.py       # URL → parser lookup
    │   └── domains/          # Domain-specific parser implementations
    │       ├── wikipedia.py
    │       ├── espn.py
    │       ├── cnbc.py
    │       └── xe.py
    ├── evaluation/
    │   ├── tokens.py         # strip_markdown, extract_unique_tokens
    │   ├── token_level.py    # Set-based metrics: precision, recall, F1
    │   └── similarity.py     # Vector-based metrics: cosine, Jaccard, excess ratio
    └── gold_standard/
        ├── urls.py           # Domain/URL listing from gs_data/
        └── gold.py           # Gold text lookup
```

## REST API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/parse?url=` | Crawl + parse a URL |
| POST | `/parse` | Parse provided `{url, html_text}` without crawling |
| GET | `/domains` | List supported domains |
| GET | `/gold_standard?url=` | Gold standard entry for a URL |
| GET | `/full_gold_standard?domain=` | All GS entries for a domain |
| POST | `/evaluate` | Score `{parsed_text, gold_text}` |
| GET | `/gs_urls` | List all gold standard URLs |
| GET | `/gold_text?url=` | Gold standard text (no crawl) |
| GET | `/full_gs_eval?domain=` | Averaged scores across all GS entries for a domain |

Errors: `400` unsupported domain · `404` URL not in GS · `503` unreachable URL.

## Supported domains

Gold standard data lives in `gs_data/`. A domain is supported when it has a corresponding `<domain>_gs.json` file there. Currently supported: Italian Wikipedia, ESPN, CNBC, XE.

## Metrics

Both the parsed text and the gold standard are stripped of markdown before scoring.

### Token Level Eval — set-based

Unique token sets (whitespace splitting after markdown stripping):

| Metric | Formula | Meaning |
|--------|---------|---------|
| **Precision** | `\|parsed ∩ gold\| / \|parsed\|` | How much of the extracted content is relevant |
| **Recall** | `\|parsed ∩ gold\| / \|gold\|` | How much of the gold content was extracted |
| **F1** | `2 · P · R / (P + R)` | Harmonic mean of precision and recall |

### Similarity Eval — frequency-vector-based

Operates on token frequency vectors (Counter), more sensitive to repeated terms and extra content:

| Metric | Formula | Meaning |
|--------|---------|---------|
| **Cosine** | `(A·B) / (\|A\|·\|B\|)` | Frequency-distribution similarity; high even when extra content is present |
| **Jaccard** | `\|A ∩ B\| / \|A ∪ B\|` | Set overlap over union; penalises both extra and missing tokens |
| **Excess Ratio** | `1 − Σ min(fp[t], fg[t]) / Σ fp[t]` | Fraction of extracted tokens not covered by gold — **lower is better** |

---

## Grader — Lab Exam 1

Computer Engineering Laboratory — A.Y. 2025/2026

Download the grader image from Classroom, then follow the steps below.

### Instructions

1. Load the grader Docker image:

    ```bash
    docker load -i lab-grader-esonero.tar.gz
    ```

2. Start your project:

    ```bash
    docker compose up --build -d
    ```

3. Run the grader with your student ID:

    ```bash
    docker run --network host lab-grader-esonero-1:1.0.1 <your_student_id>
    ```
