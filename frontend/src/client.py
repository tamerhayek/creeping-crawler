import os

import requests

BACKEND = os.environ.get("BACKEND_URL", "http://127.0.0.1:8003")


def get_gs_urls() -> list[str]:
    try:
        return requests.get(f"{BACKEND}/gs_urls", timeout=5).json().get("urls", [])
    except Exception:
        return []


def parse_url(url: str) -> tuple[dict, str | None]:
    """Returns (data, error). On success error is None."""
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
    try:
        resp = requests.get(f"{BACKEND}/gold_text", params={"url": url}, timeout=5)
        if resp.status_code == 200:
            return resp.json()["gold_text"]
    except Exception:
        pass
    return None


def evaluate(parsed_text: str, gold_text: str) -> dict | None:
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
