from pathlib import Path


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
