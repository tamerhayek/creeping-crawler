"""Gold standard URL and domain management.

Reads all GS entries from the gs_data/ directory (JSON files, one per domain).
The gs_data/ path is resolved automatically:
  - In Docker: mounted at /gs_data
  - Locally:   four levels up from this file → project root / gs_data
"""

import json
from pathlib import Path
from urllib.parse import urlparse


def _gs_data_dir() -> Path:
    """Return the path to the gs_data/ directory."""
    docker_path = Path("/gs_data")
    if docker_path.exists():
        return docker_path
    # gold_standard/ → lib/ → src/ → backend/ → project root
    return Path(__file__).resolve().parents[4] / "gs_data"


def get_all_entries() -> list[dict]:
    """Load and return all gold standard entries from every *_gs.json file."""
    entries = []
    for json_file in _gs_data_dir().glob("*_gs.json"):
        text = json_file.read_text(encoding="utf-8").strip()
        if not text:
            continue
        entries.extend(json.loads(text))
    return entries


def get_available_urls() -> list[str]:
    """Return a sorted list of all URLs present in the gold standard."""
    return sorted({e["url"] for e in get_all_entries()})


def get_domains() -> list[str]:
    """Return a sorted list of all supported domains (netloc of GS URLs)."""
    return sorted({urlparse(url).netloc for url in get_available_urls()})


def is_supported_domain(domain: str) -> bool:
    """Return True if the domain has at least one gold standard entry."""
    return domain in get_domains()


def get_urls_for_domain(domain: str) -> list[str]:
    """Return all GS URLs belonging to the given domain."""
    return [url for url in get_available_urls() if urlparse(url).netloc == domain]
