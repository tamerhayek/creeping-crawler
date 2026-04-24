"""
Crawl all URLs from gs_data using the domain configs in src/lib/crawling/configs/
and save results to gs_results/.

Run from the project root:
    make crawl

Output structure:
  ../gs_results/
    html/           <- result.html, single line in quotes, .txt (JSON-ready)
    cleaned_html/   <- result.cleaned_html, multiline, .html
    markdown/       <- result.markdown, multiline, .md

Files are overwritten on each run.
"""

import asyncio
import json
import re
import sys
from pathlib import Path

# Allow importing from src/ without installing the package
sys.path.insert(0, str(Path(__file__).parent))

from crawl4ai import AsyncWebCrawler

from src.lib.crawling.configs.registry import config_for

GS_DIR      = Path(__file__).parent.parent / "gs_data"
OUT_DIR     = Path(__file__).parent.parent / "gs_results"
HTML_DIR    = OUT_DIR / "html"
CLEANED_DIR = OUT_DIR / "cleaned_html"
MD_DIR      = OUT_DIR / "markdown"


def url_to_slug(url: str) -> str:
    url = re.sub(r"https?://", "", url)
    url = re.sub(r"[/\?=&]", "__", url)
    url = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", url)
    return url


def collect_urls() -> list[str]:
    urls = []
    for gs_file in GS_DIR.glob("*.json"):
        for entry in json.loads(gs_file.read_text()):
            if "url" in entry:
                urls.append(entry["url"])
    return urls


async def crawl_all(urls: list[str]):
    for d in (HTML_DIR, CLEANED_DIR, MD_DIR):
        d.mkdir(parents=True, exist_ok=True)

    async with AsyncWebCrawler() as crawler:
        for url in urls:
            print(f"Crawling: {url}")
            try:
                result = await crawler.arun(url=url, config=config_for(url))
            except Exception as e:
                print(f"  ERROR: {e}")
                continue

            if not result.success:
                print(f"  FAILED: {result.error_message}")
                continue

            slug = url_to_slug(url)

            # HTML — single line, inner quotes escaped, wrapped in "" for JSON
            raw = (result.html or "").replace("\n", "").replace("\r", "").replace('"', '\\"')
            (HTML_DIR / f"{slug}.txt").write_text(f'"{raw}"', encoding="utf-8")

            # Cleaned HTML — multiline
            (CLEANED_DIR / f"{slug}.html").write_text(result.cleaned_html or "", encoding="utf-8")

            # Markdown — multiline
            md = result.markdown
            if hasattr(md, "raw_markdown"):
                md = md.raw_markdown or ""
            (MD_DIR / f"{slug}.md").write_text(md or "", encoding="utf-8")

            print(f"  -> gs_results/html/{slug}.txt")
            print(f"  -> gs_results/cleaned_html/{slug}.html")
            print(f"  -> gs_results/markdown/{slug}.md")


if __name__ == "__main__":
    urls = collect_urls()
    print(f"Found {len(urls)} URLs\n")
    asyncio.run(crawl_all(urls))
