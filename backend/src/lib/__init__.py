"""Internal library for the Crawl4AI Evaluation API."""

from .crawling.crawler import fetch_page_from_html
from .gold_standard.gold import get_entry_for_url, load_gold_text
from .gold_standard.urls import get_available_urls, get_domains, get_urls_for_domain
from .parsers import get_parser_for_url
from .services import (
    assert_supported_domain,
    build_gold_entry,
    compute_similarity_eval,
    compute_token_level_eval,
    domain_of,
    fetch_page_for_url,
)
