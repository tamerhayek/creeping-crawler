"""Abstract base class for all content parsers."""

from abc import ABC, abstractmethod


class ContentParser(ABC):
    """Interface that every domain-specific parser must implement."""

    @abstractmethod
    def parse(self, url: str, markdown: str) -> str:
        """Parse raw Crawl4AI markdown and return clean text.

        Args:
            url:      the source URL, used to apply page-specific rules.
            markdown: raw markdown produced by the crawler.

        Returns:
            Clean text ready for token-level evaluation.
        """
        raise NotImplementedError
