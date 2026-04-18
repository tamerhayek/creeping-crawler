from pathlib import Path
from urllib.parse import urlparse


GS_DIR = Path("gs")


def sample_filename_to_url(filename: str) -> str:
    stem = filename.removesuffix(".txt")
    netloc, path_suffix = stem.split("_", 1)
    return f"https://{netloc}/{path_suffix.replace('_', '/')}"


def get_available_urls() -> list[str]:
    urls = [
        sample_filename_to_url(path.name)
        for path in GS_DIR.glob("*.txt")
    ]
    return sorted(urls)


def get_domains() -> list[str]:
    return sorted({urlparse(url).netloc for url in get_available_urls()})


def is_supported_domain(domain: str) -> bool:
    return domain in get_domains()


def get_urls_for_domain(domain: str) -> list[str]:
    return [url for url in get_available_urls() if urlparse(url).netloc == domain]
