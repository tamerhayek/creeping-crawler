import os

import requests
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
BACKEND = os.environ.get("BACKEND_URL", "http://127.0.0.1:8003")


def _get_gs_urls() -> list[str]:
    try:
        return requests.get(f"{BACKEND}/gs_urls", timeout=5).json().get("urls", [])
    except Exception:
        return []


@app.route("/")
def index():
    return render_template("index.html.jinja", gs_urls=_get_gs_urls())


@app.route("/compare")
def compare():
    url = request.args.get("url", "").strip()
    if not url:
        return redirect(url_for("index"))

    gs_urls = _get_gs_urls()
    error = None
    data: dict = {}

    try:
        parse_resp = requests.get(f"{BACKEND}/parse", params={"url": url}, timeout=60)
        if parse_resp.status_code != 200:
            error = parse_resp.json().get("detail", f"Backend error {parse_resp.status_code}")
        else:
            data = parse_resp.json()
            if url in gs_urls:
                gt_resp = requests.get(f"{BACKEND}/gold_text", params={"url": url}, timeout=5)
                if gt_resp.status_code == 200:
                    gold_text = gt_resp.json()["gold_text"]
                    eval_resp = requests.post(
                        f"{BACKEND}/evaluate",
                        json={"parsed_text": data["parsed_text"], "gold_text": gold_text},
                        timeout=5,
                    )
                    data["gold_text"] = gold_text
                    if eval_resp.status_code == 200:
                        data["metrics"] = eval_resp.json()["token_level_eval"]
    except requests.exceptions.ConnectionError:
        error = "Cannot connect to backend. Make sure it is running on port 8003."
    except Exception as e:
        error = str(e)

    return render_template("result.html.jinja", url=url, data=data, error=error, gs_urls=gs_urls)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8004)
