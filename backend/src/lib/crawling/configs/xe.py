"""Crawler config for www.xe.com."""

from crawl4ai import CrawlerRunConfig

CONFIG = CrawlerRunConfig(
    magic=True,
    excluded_tags=["style", "script", "link", "meta", "noscript"],
    excluded_selector=(
        # Main site header (logo, nav, get-the-app button)
        "#siteHeader, "
        # Breadcrumb bar fixed below the header
        "div[class*='fixed inset-x-0'], "
        # Blog category navigation bar (Blog / Money Transfer / Personal Finance / etc.)
        "div[class*='border-[#ccc]'], "
        # Article hero image
        "img[alt='heading picture'], "
        # Author name + date/read-time row
        "div[class*='mb-8 mt-6 flex items-center'], "
        # Table of Contents box
        "div[class*='rounded-xl bg-gray-250'], "
        # Inline CTA / signup banner links embedded in article body
        "a[href*='account.xe.com'], "
        # CTA buttons (e.g. "Create a free business account", "Speak to an FX specialist")
        "[class*='polymorphic-btn'], "
        # Article tag chips at the bottom of the post
        "div[class*='flex flex-wrap gap-2'], "
        # Blue business-promo banner after the article body
        "div[class*='min-h-[456px]'], "
        # Related articles grid section
        "section[class*='py-12'], "
        # Site-wide footer
        "footer, "
        # Cookie / GDPR consent popup
        "div[class*='animate-slideFromLeft']"
    ),
    remove_forms=True,
)
