from abc import ABC, abstractmethod


class ContentParser(ABC):
    @abstractmethod
    def parse(self, url: str, markdown: str) -> str:
        raise NotImplementedError
