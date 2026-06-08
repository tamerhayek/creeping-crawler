"""MariaDB connection pool with startup retry.

Configuration is read from environment variables:
    DB_HOST     hostname  (default: localhost)
    DB_PORT     port      (default: 3306)
    DB_NAME     database  (default: creeping_crawler)
    DB_USER     username  (default: creeping_crawler)
    DB_PASSWORD password  (default: creeping_crawler)

The pool is created lazily on the first ``init_pool()`` call. ``get_connection()``
is a context manager that borrows a connection from the pool and returns it on exit.
"""

import os
import time
from contextlib import contextmanager
from typing import Iterator

import mariadb

CONNECTION_POOL_SIZE = 5
CONNECTION_POOL_NAME = "creeping-crawler-pool"

_connection_pool: mariadb.ConnectionPool | None = None


def _database_config() -> dict:
    """Read DB_* settings from the environment."""
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", "3306")),
        "user": os.environ.get("DB_USER", "creeping_crawler"),
        "password": os.environ.get("DB_PASSWORD", "creeping_crawler"),
        "database": os.environ.get("DB_NAME", "creeping_crawler"),
    }


def init_pool(max_attempts: int = 60, delay_seconds: float = 2.0) -> None:
    """Create the connection pool, retrying until MariaDB is reachable.

    Called once at FastAPI startup. The backend container can start before
    MariaDB is ready, so we poll the server until it accepts connections.
    """
    global _connection_pool
    if _connection_pool is not None:
        return

    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            _connection_pool = mariadb.ConnectionPool(
                pool_name=CONNECTION_POOL_NAME,
                pool_size=CONNECTION_POOL_SIZE,
                pool_reset_connection=False,
                **_database_config(),
            )
            return
        except mariadb.Error as error:
            last_error = error
            print(
                f"[db] connection attempt {attempt}/{max_attempts} failed: {error}",
                flush=True,
            )
            time.sleep(delay_seconds)

    raise RuntimeError(f"MariaDB unreachable after {max_attempts} attempts: {last_error}")


def close_pool() -> None:
    """Close the pool on application shutdown."""
    global _connection_pool
    if _connection_pool is not None:
        _connection_pool.close()
        _connection_pool = None


@contextmanager
def get_connection() -> Iterator[mariadb.Connection]:
    """Borrow a connection from the pool for the duration of the with-block."""
    if _connection_pool is None:
        raise RuntimeError("Connection pool not initialized; call init_pool() first")
    connection = _connection_pool.get_connection()
    try:
        yield connection
    finally:
        connection.close()


def ping() -> bool:
    """Return True if the database is reachable, False otherwise.

    Used by the /status endpoint to report database health without raising.
    """
    if _connection_pool is None:
        return False
    try:
        with get_connection() as connection:
            connection.ping()
        return True
    except mariadb.Error:
        return False
