"""Gold standard data access.

Provides lookup functions over the GS entries loaded from gs_data/.
Each entry is a dict with at least: url, domain, title, html_text, gold_text.
"""

from .tokens import extract_unique_tokens
from .urls import get_all_entries


def get_entry_for_url(url: str) -> dict | None:
    """Return the gold standard entry for the given URL, or None if not found."""
    return next((e for e in get_all_entries() if e["url"] == url), None)


def load_gold_text(url: str) -> str | None:
    """Return the gold_text field for the given URL, or None if not found."""
    entry = get_entry_for_url(url)
    return entry.get("gold_text") if entry else None


def load_gold_tokens(url: str) -> set[str]:
    """Return the set of unique tokens from the gold text of the given URL."""
    text = load_gold_text(url)
    return extract_unique_tokens(text) if text else set()
