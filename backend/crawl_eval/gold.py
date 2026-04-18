from pathlib import Path
from urllib.parse import urlparse

from .tokens import extract_unique_tokens


GS_DIR = Path("gs")


def gold_sample_path_for_url(url: str) -> Path:
    parsed = urlparse(url)
    sample_name = f"{parsed.netloc}{parsed.path}".strip("/").replace("/", "_") + ".txt"
    return GS_DIR / sample_name


def load_sample_text(sample_path: Path) -> str:
    return sample_path.read_text(encoding="utf-8")


def load_sample_tokens(sample_path: Path) -> set[str]:
    return extract_unique_tokens(load_sample_text(sample_path))
