"""Internal library for the Crawl4AI Evaluation API."""

from .crawling.crawler import fetch_page, fetch_page_from_html, fetch_page_for_url
from .evaluation.similarity import calculate_content_metrics
from .evaluation.token_level import calculate_token_level_metrics
from .gold_standard.gold import get_entry_for_url, load_gold_text
from .gold_standard.urls import get_available_urls, get_domains, get_urls_for_domain
from .parsers import get_parser_for_url
from .utils import assert_supported_domain, domain_of
