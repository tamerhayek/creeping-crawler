"""FastAPI application entry point.

Run from the backend/ directory:
    uvicorn src.server:app --host 0.0.0.0 --port 8003

Startup sequence (lifespan):
    1. wait for MariaDB and open the connection pool
    2. seed the gold standard tables from gs_data/ on first boot
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .lib.db import close_pool, init_pool, populate_if_empty
from .routes import domains_router, evaluate_router, gold_router, parse_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_pool()
    inserted_count = populate_if_empty()
    if inserted_count:
        print(f"[startup] seeded {inserted_count} gold standard entries", flush=True)
    yield
    close_pool()


app = FastAPI(title="Creeping Crawler API", lifespan=lifespan)

app.include_router(domains_router)
app.include_router(parse_router)
app.include_router(gold_router)
app.include_router(evaluate_router)
