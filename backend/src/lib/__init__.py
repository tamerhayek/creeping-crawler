"""Internal library for the Crawl4AI Evaluation API."""

from .crawling.crawler import fetch_page, fetch_page_from_html, PageContent
from .evaluation.metrics import TokenLevelMetrics, calculate_cosine_similarity, calculate_token_level_metrics

from .evaluation.tokens import extract_unique_tokens, strip_markdown
from .gold_standard.gold import get_entry_for_url, load_gold_text, load_gold_tokens
from .gold_standard.urls import (
    get_all_entries,
    get_available_urls,
    get_domains,
    get_urls_for_domain,
    is_supported_domain,
)
from .parsers import get_parser_for_url
from .services import (
    assert_supported_domain,
    build_gold_entry,
    compute_token_count_eval,
    compute_token_level_eval,
    domain_of,
    fetch_page_for_url,
)
