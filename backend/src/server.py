"""FastAPI application entry point.

Run from the backend/ directory:
    uvicorn src.server:app --host 0.0.0.0 --port 8003
"""

from fastapi import FastAPI

from .routes import domains_router, evaluate_router, gold_router, parse_router

app = FastAPI(title="Crawl4AI Evaluation API")

app.include_router(domains_router)
app.include_router(parse_router)
app.include_router(gold_router)
app.include_router(evaluate_router)
