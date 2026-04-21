from .tokens import extract_unique_tokens
from .urls import get_all_entries

def get_entry_for_url(url: str) -> dict | None:
    return next((e for e in get_all_entries() if e["url"] == url), None)

def load_gold_text(url: str) -> str | None:
    entry = get_entry_for_url(url)
    return entry.get("gold_text") if entry else None

def load_gold_tokens(url: str) -> set[str]:
    text = load_gold_text(url)
    return extract_unique_tokens(text) if text else set()
