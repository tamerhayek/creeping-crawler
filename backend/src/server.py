from fastapi import FastAPI

from .routes import domains_router, evaluate_router, gold_router, parse_router

app = FastAPI(title="Crawl4AI Evaluation API")

app.include_router(domains_router)
app.include_router(parse_router)
app.include_router(gold_router)
app.include_router(evaluate_router)
