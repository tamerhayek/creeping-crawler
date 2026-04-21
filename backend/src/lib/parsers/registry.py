"""Parser registry: maps URL hostnames to their ContentParser implementation.

To add a new domain parser:
  1. Create a new class in a dedicated module (e.g. parsers/reddit.py).
  2. Import it here and add a branch in get_parser_for_url().
"""

from urllib.parse import urlparse

from .base import ContentParser
from .default import PassThroughParser
from .wikipedia import WikipediaParser


def get_parser_for_url(url: str) -> ContentParser:
    """Return the appropriate parser for the given URL.

    Falls back to PassThroughParser for unrecognised domains.
    """
    hostname = urlparse(url).netloc.lower()

    if hostname.endswith("wikipedia.org"):
        return WikipediaParser()

    return PassThroughParser()
