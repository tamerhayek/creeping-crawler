"""Crawler-config registry: maps URL hostnames to their CrawlerRunConfig.

To add a new domain:
  1. Create a module in this package (e.g. configs/reddit.py) that exposes CONFIG.
  2. Import it here and add an entry in DOMAIN_CONFIGS.
"""

from urllib.parse import urlparse

from crawl4ai import CrawlerRunConfig

from . import cnbc, espn, wikipedia, xe
from .default import CONFIG as _DEFAULT_CONFIG

DOMAIN_CONFIGS: dict[str, CrawlerRunConfig] = {
    "it.wikipedia.org": wikipedia.CONFIG,
    "www.espn.com": espn.CONFIG,
    "www.cnbc.com": cnbc.CONFIG,
    "www.xe.com": xe.CONFIG,
}


def config_for(url: str) -> CrawlerRunConfig:
    """Return the crawler config for the given URL's domain."""
    return DOMAIN_CONFIGS.get(urlparse(url).netloc.lower(), _DEFAULT_CONFIG)
