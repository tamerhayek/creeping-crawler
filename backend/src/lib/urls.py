import json
from pathlib import Path
from urllib.parse import urlparse

def _gs_data_dir() -> Path:
    docker_path = Path("/gs_data")
    if docker_path.exists():
        return docker_path
    return Path(__file__).resolve().parents[3] / "gs_data"

def get_all_entries() -> list[dict]:
    entries = []
    for json_file in _gs_data_dir().glob("*_gs.json"):
        text = json_file.read_text(encoding="utf-8").strip()
        if not text:
            continue
        entries.extend(json.loads(text))
    return entries

def get_available_urls() -> list[str]:
    return sorted({e["url"] for e in get_all_entries()})

def get_domains() -> list[str]:
    return sorted({urlparse(url).netloc for url in get_available_urls()})

def is_supported_domain(domain: str) -> bool:
    return domain in get_domains()

def get_urls_for_domain(domain: str) -> list[str]:
    return [url for url in get_available_urls() if urlparse(url).netloc == domain]
