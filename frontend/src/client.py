"""HTTP client for the backend API.

All communication with the backend goes through this module.
BACKEND_URL defaults to localhost:8003 and can be overridden via the
BACKEND_URL environment variable (set in docker-compose.yml for Docker).
"""

import os

import requests

BACKEND = os.environ.get("BACKEND_URL", "http://127.0.0.1:8003")


def get_gs_urls() -> list[str]:
    """Return all gold standard URLs from the backend.

    Returns an empty list if the backend is unreachable.
    """
    try:
        return requests.get(f"{BACKEND}/gs_urls", timeout=5).json().get("urls", [])
    except Exception:
        return []


def parse_url(url: str) -> tuple[dict, str | None]:
    """Crawl and parse a URL via the backend /parse endpoint.

    Returns:
        (data, None)  on success — data contains url, domain, title,
                      html_text, and parsed_text.
        ({}, error)   on failure — error is a human-readable message.
    """
    try:
        resp = requests.get(f"{BACKEND}/parse", params={"url": url}, timeout=60)
        if resp.status_code != 200:
            return {}, resp.json().get("detail", f"Backend error {resp.status_code}")
        return resp.json(), None
    except requests.exceptions.ConnectionError:
        return {}, "Cannot connect to backend. Make sure it is running on port 8003."
    except Exception as e:
        return {}, str(e)


def get_gold_text(url: str) -> str | None:
    """Return the gold standard text for the given URL, or None if unavailable."""
    try:
        resp = requests.get(f"{BACKEND}/gold_text", params={"url": url}, timeout=5)
        if resp.status_code == 200:
            return resp.json()["gold_text"]
    except Exception:
        pass
    return None


def evaluate(parsed_text: str, gold_text: str) -> dict | None:
    """Compute token-level evaluation metrics via the backend /evaluate endpoint.

    Returns:
        A dict with precision, recall, and f1 keys, or None on failure.
    """
    try:
        resp = requests.post(
            f"{BACKEND}/evaluate",
            json={"parsed_text": parsed_text, "gold_text": gold_text},
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()["token_level_eval"]
    except Exception:
        pass
    return None
