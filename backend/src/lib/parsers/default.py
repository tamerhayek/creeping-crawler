from .base import ContentParser


class PassThroughParser(ContentParser):
    def parse(self, url: str, markdown: str) -> str:
        return markdown
