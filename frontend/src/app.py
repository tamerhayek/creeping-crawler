from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import compare_router, index_router

app = FastAPI(title="Crawl4AI Eval Frontend")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(index_router)
app.include_router(compare_router)
