"""Gold standard URL and domain queries.

Supported domains are read from ``domains.json`` (a domain is "supported"
when a dedicated parser exists for it). Gold standard URLs themselves are
read from the ``gold_standard`` table in MariaDB; the table is seeded from
``gs_data/*_gs.json`` at first boot by ``db.init_loader``.
"""

import json
from pathlib import Path

from ..db import queries


def _domains_file() -> Path:
    """Return the path to domains.json."""
    docker_path = Path("/app/domains.json")
    if docker_path.exists():
        return docker_path
    # gold_standard/ → lib/ → src/ → backend/ → project root
    return Path(__file__).resolve().parents[4] / "domains.json"


def get_domains() -> list[str]:
    """Return the list of supported domains from domains.json."""
    return json.loads(_domains_file().read_text(encoding="utf-8"))["domains"]


def is_supported_domain(domain: str) -> bool:
    """Return True if the domain has a dedicated parser."""
    return domain in get_domains()


def get_urls_for_domain(domain: str) -> list[str]:
    """Return all GS URLs belonging to the given domain."""
    return queries.get_urls_by_domain(domain)
