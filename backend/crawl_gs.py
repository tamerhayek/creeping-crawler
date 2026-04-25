"""
Crawl gold standard URLs and save results to gs_results/ for manual inspection.
Optionally updates html_text in-place in the gs_data/ JSON files.

Usage (via Makefile):
    make crawl                                        # all domains
    make crawl -- --domain www.xe.com                 # single domain
    make crawl -- --update-json                       # all domains + update JSON
    make crawl -- --domain www.xe.com --update-json   # single domain + update JSON

Or directly:
    python crawl_gs.py [--domain DOMAIN] [--update-json]

Output structure:
  ../gs_results/
    html/           <- result.html, prettified
    cleaned_html/   <- result.cleaned_html, prettified
    markdown/       <- result.markdown, .md file
"""

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

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


def prettify_html(html: str) -> str:
    """Return a prettified (indented, multi-line) version of the HTML."""
    return BeautifulSoup(html, "lxml").prettify()


def html_for_json(html: str) -> str:
    """Return HTML as a single-line string safe for embedding in JSON."""
    return html.replace("\n", "").replace("\r", "")


async def crawl_all(update_json: bool = False, domain: str | None = None):
    for d in (HTML_DIR, CLEANED_DIR, MD_DIR):
        d.mkdir(parents=True, exist_ok=True)

    # Load all gs files and index entries by URL
    gs_files: dict[Path, list[dict]] = {}
    url_to_file: dict[str, Path] = {}
    for gs_file in sorted(GS_DIR.glob("*.json")):
        entries = json.loads(gs_file.read_text())
        gs_files[gs_file] = entries
        for entry in entries:
            if "url" in entry:
                url_to_file[entry["url"]] = gs_file

    if domain is not None:
        filtered = {url: f for url, f in url_to_file.items() if domain in url}
        if not filtered:
            print(f"ERROR: domain '{domain}' not found in any gold standard file.", file=sys.stderr)
            sys.exit(1)
        url_to_file = filtered

    urls = list(url_to_file.keys())
    print(f"Found {len(urls)} URLs\n")

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
            html = result.html or ""

            # gs_results/html/ — prettified multiline HTML file
            (HTML_DIR / f"{slug}.html").write_text(prettify_html(html), encoding="utf-8")

            # gs_results/cleaned_html/ — prettified multiline HTML file
            cleaned = result.cleaned_html or ""
            (CLEANED_DIR / f"{slug}.html").write_text(prettify_html(cleaned) if cleaned else "", encoding="utf-8")

            # gs_results/markdown/ — markdown file
            md = result.markdown
            if hasattr(md, "raw_markdown"):
                md = md.raw_markdown or ""
            (MD_DIR / f"{slug}.md").write_text(md or "", encoding="utf-8")

            print(f"  -> gs_results/html/{slug}.html")
            print(f"  -> gs_results/cleaned_html/{slug}.html")
            print(f"  -> gs_results/markdown/{slug}.md")

            if update_json:
                gs_file = url_to_file[url]
                for entry in gs_files[gs_file]:
                    if entry["url"] == url:
                        entry["html_text"] = html_for_json(html)
                        break
                print(f"  -> html_text updated in {gs_file.name}")

    if update_json:
        for gs_file, entries in gs_files.items():
            gs_file.write_text(json.dumps(entries, ensure_ascii=False, indent="\t"), encoding="utf-8")
            print(f"\nSaved: {gs_file.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl gold standard URLs.")
    parser.add_argument(
        "--update-json",
        action="store_true",
        help="Also update html_text in the gs_data JSON files.",
    )
    parser.add_argument(
        "--domain",
        metavar="DOMAIN",
        help="Crawl only URLs belonging to this domain (e.g. www.xe.com).",
    )
    args = parser.parse_args()
    asyncio.run(crawl_all(update_json=args.update_json, domain=args.domain))
