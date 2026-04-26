"""Crawler config for www.cnbc.com."""

from crawl4ai import CrawlerRunConfig

CONFIG = CrawlerRunConfig(
    magic=True,
    excluded_tags=["style", "script", "link", "meta", "noscript"],
    excluded_selector=(
        # Global navigation & menus
        "#GlobalNavigation, "
        "[class*='CNBCGlobalNav'], "
        "[class*='nav-menu-'], "
        # Account / sign-in / sign-up
        "[class*='account-menu'], "
        "[class*='SignInMenu'], "
        "[class*='SignUpMenu'], "
        # Skip / jump links
        "[class*='JumpLink'], "
        # Watch-live button
        "[class*='WatchLive'], "
        # Cookie consent (OneTrust)
        "#onetrust-consent-sdk, #onetrust-banner-sdk, "
        "#onetrust-pc-sdk, .otFlat, .ot-iab-2, "
        # Article eyebrow (category breadcrumb) and publish date
        "[class*='ArticleHeader-eyebrow'], "
        "[class*='ArticleHeader-time'], "
        # Author info block
        "[class*='Author-author'], "
        "[class*='ArticleHeader-authorAndShareInline'], "
        # Inline video embeds
        "[class*='InlineVideo'], "
        "[class*='PlaceHolder-wrapper'], "
        # Inline image embeds
        "[class*='InlineImage-imageEmbed'], "
        # Stock ticker / related quotes widget and inline ticker buttons
        ".RelatedQuotes-relatedQuotes, "
        "[class*='QuoteInBody-inlineButton'], "
        # "Choose CNBC as your preferred source" banner
        "[class*='googlePreferredSourceContainer'], "
        # Special-report topic navigation
        "[class*='PageHeaderWithTuneInText'], "
        # Transporter / recommended-articles sections
        "[class*='TransporterSection'], "
        "[class*='SectionWrapper'], "
        # Global footer
        "#GlobalFooter, [class*='CNBCFooter']"
    ),
    remove_forms=True,
)
