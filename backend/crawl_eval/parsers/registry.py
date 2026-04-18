from urllib.parse import urlparse

from .base import ContentParser
from .default import PassThroughParser
from .wikipedia import WikipediaParser


def get_parser_for_url(url: str) -> ContentParser:
    hostname = urlparse(url).netloc.lower()

    if hostname.endswith("wikipedia.org"):
        return WikipediaParser()

    return PassThroughParser()
