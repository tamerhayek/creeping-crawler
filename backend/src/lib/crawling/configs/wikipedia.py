"""Crawler config for it.wikipedia.org."""

from crawl4ai import CrawlerRunConfig

CONFIG = CrawlerRunConfig(
    magic=True,
    excluded_tags=["style", "script", "link", "meta", "noscript"],
    excluded_selector=(
        # Infobox / sinottico
        "table.infobox, table.sinottico, "
        ".itwiki-template-occhiello, itwiki-template-citazione-footer, "
        # Short description and hatnote
        ".shortdescription, .hatnote, "
        # Interlanguage links block ("N lingue")
        "#p-lang-btn, .mw-portlet-lang, .after-portlet-lang, "
        # Table of contents (Vector skin variants)
        ".toc, .vector-toc, .vector-page-titlebar-toc, #vector-toc, "
        # Navbox and navigation templates
        ".navbox, .vertical-navbox, "
        # Maintenance / warning banners
        ".ambox, .tmbox, .ombox, .cmbox, .fmbox, "
        # Metadata, edit section links, references
        ".metadata, .mw-editsection, "
        ".reflist, .mw-references, sup.reference, mw-ref, reference, "
        # Categories
        "#catlinks, "
        # Site header, sticky header, page toolbar
        ".vector-header-container, .vector-header, .mw-header, "
        ".vector-sticky-header-container, .vector-sticky-header, "
        ".vector-page-toolbar, .vector-page-tools, "
        # Site notices and banners
        ".vector-sitenotice-container, #siteNotice, #centralNotice, "
        ".mw-dismissable-notice, #localNotice, .anonnotice, "
        # Pre-content area ("Da Wikipedia, l'enciclopedia libera")
        ".vector-body-before-content, #siteSub, "
        # Sister-project boxes, portal bars, side boxes
        ".sistersitebox, .portal-bar, .side-box, "
        # Image captions
        "figcaption, "
        # Inline annotation markers (chiarimento, noprint apices)
        ".chiarimento, sup.noprint, "
        # Footer
        ".mw-footer-container, .mw-footer, #footer, .printfooter"
    ),
    remove_forms=True,
)
