import re


def extract_unique_tokens(text: str) -> set[str]:
    normalized = text.replace("\n", " ")
    return {token for token in normalized.split(" ") if token}


def strip_markdown(text: str) -> str:
    """Remove markdown formatting, leaving only plain text content."""
    # Images (before links)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]*\)', r'\1', text)
    # Links [text](url) -> text
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
    # Headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Bold/italic (*** ** * ___ __ _)
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'_{1,3}(.*?)_{1,3}', r'\1', text, flags=re.DOTALL)
    # Inline code
    text = re.sub(r'`([^`]*)`', r'\1', text)
    # Horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    return text
