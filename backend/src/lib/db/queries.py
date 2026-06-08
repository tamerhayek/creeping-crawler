"""SQL queries over web_resources and gold_standard.

All queries use ``?`` placeholders for parameters; no string interpolation
of user-controlled values. Read queries return Pydantic models defined in
``models.py``.
"""

from urllib.parse import urlparse

from .connection import get_connection
from .models import GoldStandardEntry, WebResource


# ─── Read ────────────────────────────────────────────────────────────────────

def get_resource(url: str) -> WebResource | None:
    """Return the web_resources row for the URL, or None."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT url, domain, title, html_text FROM web_resources WHERE url = ?",
            (url,),
        )
        row = cursor.fetchone()
    if row is None:
        return None
    return WebResource(url=row[0], domain=row[1], title=row[2] or "", html_text=row[3])


def get_gold_standard(url: str) -> GoldStandardEntry | None:
    """Return the gold standard entry joined with its web resource, or None."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT w.url, w.domain, w.title, w.html_text, g.gold_text
            FROM gold_standard g
            JOIN web_resources w ON w.url = g.url
            WHERE g.url = ?
            """,
            (url,),
        )
        row = cursor.fetchone()
    if row is None:
        return None
    return GoldStandardEntry(
        url=row[0],
        domain=row[1],
        title=row[2] or "",
        html_text=row[3],
        gold_text=row[4],
    )


def get_all_urls() -> list[str]:
    """Return every URL present in the gold_standard table (sorted)."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT url FROM gold_standard ORDER BY url")
        return [row[0] for row in cursor.fetchall()]


def get_urls_by_domain(domain: str) -> list[str]:
    """Return all gold standard URLs belonging to a domain (sorted)."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT w.url FROM gold_standard g
            JOIN web_resources w ON w.url = g.url
            WHERE w.domain = ? ORDER BY w.url
            """,
            (domain,),
        )
        return [row[0] for row in cursor.fetchall()]


def get_entries_by_domain(domain: str) -> list[GoldStandardEntry]:
    """Return all gold standard entries for a domain, joined with web_resources."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT w.url, w.domain, w.title, w.html_text, g.gold_text
            FROM gold_standard g
            JOIN web_resources w ON w.url = g.url
            WHERE w.domain = ? ORDER BY w.url
            """,
            (domain,),
        )
        return [
            GoldStandardEntry(
                url=row[0],
                domain=row[1],
                title=row[2] or "",
                html_text=row[3],
                gold_text=row[4],
            )
            for row in cursor.fetchall()
        ]


# ─── Counts (for /db_stats) ──────────────────────────────────────────────────

def count_resources() -> int:
    """Total number of web_resources rows."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM web_resources")
        return cursor.fetchone()[0]


def count_resources_per_domain() -> dict[str, int]:
    """Number of web_resources rows grouped by domain."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT domain, COUNT(*) FROM web_resources GROUP BY domain")
        return {row[0]: row[1] for row in cursor.fetchall()}


def count_gold_per_domain() -> dict[str, int]:
    """Number of gold_standard rows grouped by their resource's domain."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT w.domain, COUNT(*) FROM gold_standard g
            JOIN web_resources w ON w.url = g.url
            GROUP BY w.domain
            """
        )
        return {row[0]: row[1] for row in cursor.fetchall()}


# ─── Write ───────────────────────────────────────────────────────────────────

def add_resource(url: str, html_text: str, title: str = "") -> None:
    """Insert or overwrite a web_resources row. Domain is derived from url."""
    domain = urlparse(url).netloc
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO web_resources (url, domain, title, html_text)
            VALUES (?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE
                domain = VALUES(domain),
                title = VALUES(title),
                html_text = VALUES(html_text)
            """,
            (url, domain, title, html_text),
        )
        connection.commit()


def add_gold_standard(url: str, gold_text: str) -> bool:
    """Insert or overwrite a gold_standard row.

    Returns False if no matching web_resources row exists (FK would fail).
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM web_resources WHERE url = ?", (url,))
        if cursor.fetchone() is None:
            return False
        cursor.execute(
            """
            INSERT INTO gold_standard (url, gold_text)
            VALUES (?, ?)
            ON DUPLICATE KEY UPDATE gold_text = VALUES(gold_text)
            """,
            (url, gold_text),
        )
        connection.commit()
        return True


def delete_resource(url: str) -> bool:
    """Delete a web_resources row (cascades to gold_standard via FK).

    Returns True if a row was removed.
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM web_resources WHERE url = ?", (url,))
        connection.commit()
        return cursor.rowcount > 0


def delete_gold_standard(url: str) -> bool:
    """Delete only the gold_standard row. Returns True if a row was removed."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM gold_standard WHERE url = ?", (url,))
        connection.commit()
        return cursor.rowcount > 0


# ─── Bulk (init loader) ──────────────────────────────────────────────────────

def add_entries(entries: list[dict]) -> None:
    """Insert many (web_resource + gold_standard) rows in a single transaction.

    Each entry must contain: url, domain, title, html_text, gold_text.
    Existing rows are skipped (INSERT IGNORE).

    Inserts run one statement at a time (not ``executemany``): some HTML
    blobs are several MB and a bulk packet would exceed MariaDB's default
    ``max_allowed_packet`` (16 MB) and trigger a connection reset.
    """
    if not entries:
        return
    with get_connection() as connection:
        cursor = connection.cursor()
        for entry in entries:
            cursor.execute(
                """
                INSERT IGNORE INTO web_resources (url, domain, title, html_text)
                VALUES (?, ?, ?, ?)
                """,
                (entry["url"], entry["domain"], entry.get("title", ""), entry["html_text"]),
            )
            cursor.execute(
                """
                INSERT IGNORE INTO gold_standard (url, gold_text)
                VALUES (?, ?)
                """,
                (entry["url"], entry["gold_text"]),
            )
        connection.commit()


# ─── Evaluations cache ───────────────────────────────────────────────────────

def save_quantitative_eval(
    url: str,
    precision: float,
    recall: float,
    f1: float,
    cosine: float,
    jaccard: float,
    excess_ratio: float,
) -> None:
    """Upsert token-level + similarity metrics for a URL."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO evaluations (url, precision_val, recall_val, f1, cosine, jaccard, excess_ratio)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE
                precision_val = VALUES(precision_val),
                recall_val = VALUES(recall_val),
                f1 = VALUES(f1),
                cosine = VALUES(cosine),
                jaccard = VALUES(jaccard),
                excess_ratio = VALUES(excess_ratio)
            """,
            (url, precision, recall, f1, cosine, jaccard, excess_ratio),
        )
        connection.commit()


def save_judge_eval(url: str, judge_score: int) -> None:
    """Upsert the judge score for a URL."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO evaluations (url, judge_score)
            VALUES (?, ?)
            ON DUPLICATE KEY UPDATE judge_score = VALUES(judge_score)
            """,
            (url, judge_score),
        )
        connection.commit()


def get_avg_eval_per_domain() -> dict[str, dict]:
    """Return the average token-level and similarity metrics for each domain."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT w.domain,
                   AVG(e.precision_val), AVG(e.recall_val), AVG(e.f1),
                   AVG(e.cosine), AVG(e.jaccard), AVG(e.excess_ratio)
            FROM evaluations e
            JOIN web_resources w ON w.url = e.url
            WHERE e.precision_val IS NOT NULL
            GROUP BY w.domain
            """
        )
        return {
            row[0]: {
                "token_level_eval": {
                    "precision": float(row[1]),
                    "recall": float(row[2]),
                    "f1": float(row[3]),
                },
                "similarity_eval": {
                    "cosine": float(row[4]),
                    "jaccard": float(row[5]),
                    "excess_ratio": float(row[6]),
                },
            }
            for row in cursor.fetchall()
        }


def get_avg_judge_per_domain() -> dict[str, dict]:
    """Return the average judge score for each domain."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT w.domain, AVG(e.judge_score)
            FROM evaluations e
            JOIN web_resources w ON w.url = e.url
            WHERE e.judge_score IS NOT NULL
            GROUP BY w.domain
            """
        )
        return {row[0]: {"judge_score": float(row[1])} for row in cursor.fetchall()}
