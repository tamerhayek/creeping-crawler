"""Text tokenization and markdown stripping utilities.

Tokens are defined as whitespace-separated words.
This module is used for both gold standard loading and parser output evaluation.
"""

import re


def extract_unique_tokens(text: str) -> set[str]:
    """Return the set of unique whitespace-separated tokens in the text.

    Newlines are treated as spaces. Empty strings are discarded.
    """
    normalized = text.replace("\n", " ")
    return {token for token in normalized.split(" ") if token}


def strip_markdown(text: str) -> str:
    """Remove markdown syntax and return plain text content.

    Handles: images, links, headers, bold/italic, inline code,
    and horizontal rules. Used before token-level evaluation so
    that formatting characters do not affect scores.
    """
    text = re.sub(r'!\[([^\]]*)\]\([^\)]*\)', r'\1', text)               # images → alt text
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)                 # links → label
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)            # headers
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text, flags=re.DOTALL)  # bold / italic
    text = re.sub(r'_{1,3}(.*?)_{1,3}', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]*)`', r'\1', text)                              # inline code
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)        # horizontal rules
    return text
