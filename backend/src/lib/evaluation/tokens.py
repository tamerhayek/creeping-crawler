"""Text tokenization and markdown stripping utilities.

Tokens are defined as whitespace-separated words.
This module is used for both gold standard loading and parser output evaluation.
"""

import re

import mistune
from bs4 import BeautifulSoup


def extract_unique_tokens(text: str) -> set[str]:
    """Return the set of unique whitespace-separated tokens in the text.

    Newlines are treated as spaces. Empty strings are discarded.
    """
    normalized = text.replace("\n", " ")
    return {token for token in normalized.split(" ") if token}


def strip_markdown(text: str) -> str:
    """Remove markdown syntax and return plain text content.

    Converts markdown to HTML via mistune, then uses BeautifulSoup to
    extract only the text (unwrapping all tags in-place so punctuation
    and spacing are preserved). Used before token-level evaluation so
    that formatting characters do not affect scores.
    """
    html = mistune.html(text)
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(True):
        tag.unwrap()
    text = re.sub(r'[ \t]+', ' ', str(soup))   # collapse horizontal whitespace
    text = re.sub(r'\n+', '\n', text)           # collapse multiple newlines
    return text.strip()
