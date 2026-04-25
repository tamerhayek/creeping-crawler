"""Crawler config for www.espn.com."""

from crawl4ai import CrawlerRunConfig

CONFIG = CrawlerRunConfig(
    magic=True,
    excluded_tags=["style", "script", "link", "meta", "noscript"],
    excluded_selector=(
        # Global header, navigation, scoreboard ticker
        "#header-wrapper, #global-header, #global-scoreboard, "
        "#global-nav, #global-nav-mobile-trigger, "
        # Sidebar and related news feed
        ".sidebar, #news-feed-content, #news-feed, "
        # Article metadata: author bio, byline, timestamp
        ".article-meta, .byline-wrap, .byline-measured, "
        ".byline-authors, .author-overlay, .timestamp, "
        # Social share and reactions
        ".content-reactions, .share-button-wrapper, "
        ".share-popup, .content-reactions-extended-wrapper, "
        # Inline aside elements (photo, video promo, editorial box)
        "aside.inline, aside.inline-photo, aside.inline-track, "
        "aside.editorial, aside.float-r, "
        # Article footer and legal
        ".article-footer, .article-legal-footer, "
        # Cookie consent (OneTrust)
        ".ot-sdk-container, #onetrust-consent-sdk, "
        "#onetrust-button-group-parent, .ot-cat-grp"
    ),
    remove_forms=True,
)
