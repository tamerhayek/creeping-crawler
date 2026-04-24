"""Text tokenization and markdown stripping utilities.

Tokens are defined as whitespace-separated words.
This module is used for both gold standard loading and parser output evaluation.
"""

import html as html_mod
import re

import mistune
from bs4 import BeautifulSoup


def extract_unique_tokens(text: str) -> set[str]:
    """Return the set of unique whitespace-separated tokens in the text.

    Newlines are treated as spaces. Empty strings are discarded.
    """
    normalized = text.replace("\n", " ")
    return {token for token in normalized.split(" ") if token}


_QUOTE_TABLE = str.maketrans({
    '\u2018': "'",   # left single quotation mark
    '\u2019': "'",   # right single quotation mark / apostrophe
    '\u201c': '"',   # left double quotation mark
    '\u201d': '"',   # right double quotation mark
    '\u2013': '-',   # en dash
    '\u2014': '-',   # em dash
})


def strip_markdown(text: str) -> str:
    """Remove markdown syntax and return plain text content.

    Converts markdown to HTML via mistune, then uses BeautifulSoup to
    extract only the text (unwrapping all tags in-place so punctuation
    and spacing are preserved). Used before token-level evaluation so
    that formatting characters do not affect scores.

    Unicode typographic quotes and dashes are normalised to their ASCII
    equivalents so that token comparison is not sensitive to quote style.
    """
    text = text.translate(_QUOTE_TABLE)
    html = mistune.html(text)
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(True):
        tag.unwrap()
    text = re.sub(r'[ \t]+', ' ', str(soup))   # collapse horizontal whitespace
    text = re.sub(r'\n+', '\n', text)           # collapse multiple newlines
    text = html_mod.unescape(text)              # decode &amp; → & etc.
    return text.strip()
