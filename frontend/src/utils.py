"""Shared text utilities for the frontend."""

import html as html_mod
import re

import mistune
from bs4 import BeautifulSoup


_QUOTE_TABLE = str.maketrans({
    '\u2018': "'",   # left single quotation mark
    '\u2019': "'",   # right single quotation mark / apostrophe
    '\u201c': '"',   # left double quotation mark
    '\u201d': '"',   # right double quotation mark
    '\u2013': '-',   # en dash
    '\u2014': '-',   # em dash
})


def strip_markdown(text: str) -> str:
    """Convert markdown to plain text using mistune + BeautifulSoup.

    Normalises unicode typographic quotes and dashes to ASCII equivalents
    so the diff view is not polluted by quote-style differences.
    """
    text = text.translate(_QUOTE_TABLE)
    html = mistune.html(text)
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(True):
        tag.unwrap()
    text = re.sub(r'[ \t]+', ' ', str(soup))
    text = re.sub(r'\n+', '\n', text)
    text = html_mod.unescape(text)
    return text.strip()
