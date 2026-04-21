"""Frontend route registry."""

from .compare import router as compare_router
from .index import router as index_router

__all__ = ["index_router", "compare_router"]
