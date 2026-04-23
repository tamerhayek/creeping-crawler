"""
Crawl all URLs from gs_data and save result.html / result.cleaned_html to temp/.

Run from the backend/ directory:
    conda activate crawl4ai-backend
    python crawl_gs.py

Output structure:
  ../temp/
    html/           <- result.html, single line, saved as .html
    cleaned_html/   <- result.cleaned_html, pretty, saved as .html

Files are named after the URL, e.g.:
  it.wikipedia.org__wiki__BabelNet.html
"""

import asyncio
import json
import re
from pathlib import Path

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

GS_DIR = Path(__file__).parent.parent / "gs_data"
TMP_DIR = Path(__file__).parent.parent / "temp"
HTML_DIR = TMP_DIR / "html"
CLEANED_DIR = TMP_DIR / "cleaned_html"

CONFIG = CrawlerRunConfig(magic=True)


def url_to_filename(url: str) -> str:
    url = re.sub(r"https?://", "", url)
    url = re.sub(r"[/\?=&]", "__", url)
    url = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", url)
    return url + ".html"


def collect_urls() -> list[str]:
    urls = []
    for gs_file in GS_DIR.glob("*.json"):
        for entry in json.loads(gs_file.read_text()):
            if "url" in entry:
                urls.append(entry["url"])
    return urls


async def crawl_all(urls: list[str]):
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)

    async with AsyncWebCrawler() as crawler:
        for url in urls:
            print(f"Crawling: {url}")
            try:
                result = await crawler.arun(url=url, config=CONFIG)
            except Exception as e:
                print(f"  ERROR: {e}")
                continue

            if not result.success:
                print(f"  FAILED: {result.error_message}")
                continue

            filename = url_to_filename(url)

            # result.html — single line, wrapped in quotes with escaped inner quotes
            # ready to copy-paste as a JSON string value
            raw = (result.html or "").replace("\n", "").replace("\r", "").replace('"', '\\"')
            (HTML_DIR / filename.replace(".html", ".txt")).write_text(f'"{raw}"', encoding="utf-8")

            # result.cleaned_html — pretty (multiline)
            (CLEANED_DIR / filename).write_text(result.cleaned_html or "", encoding="utf-8")

            print(f"  -> temp/html/{filename.replace('.html', '.txt')}")
            print(f"  -> temp/cleaned_html/{filename}")


if __name__ == "__main__":
    urls = collect_urls()
    print(f"Found {len(urls)} URLs\n")
    asyncio.run(crawl_all(urls))
