def extract_unique_tokens(text: str) -> set[str]:
    normalized = text.replace("\n", " ")
    return {token for token in normalized.split(" ") if token}
