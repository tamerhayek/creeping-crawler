"""Shared text utilities for the frontend."""

import html as html_module
import re

import mistune
from bs4 import BeautifulSoup


QUOTE_TABLE = str.maketrans({
    "‘": "'",   # left single quotation mark
    "’": "'",   # right single quotation mark / apostrophe
    "“": '"',   # left double quotation mark
    "”": '"',   # right double quotation mark
    "–": "-",   # en dash
    "—": "-",   # em dash
})


def strip_markdown(text: str) -> str:
    """Convert markdown to plain text using mistune + BeautifulSoup.

    Normalises unicode typographic quotes and dashes to ASCII so the diff
    view is not polluted by quote-style differences.
    """
    text = text.translate(QUOTE_TABLE)
    html = mistune.html(text)
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(True):
        tag.unwrap()
    text = re.sub(r"[ \t]+", " ", str(soup))
    text = re.sub(r"\n+", "\n", text)
    text = html_module.unescape(text)
    return text.strip()
