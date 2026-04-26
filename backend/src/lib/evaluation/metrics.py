"""Re-export shim — kept for backward compatibility.

Prefer importing directly from token_level or similarity.
"""

from .token_level import TokenLevelMetrics, calculate_token_level_metrics
from .similarity import ContentMetrics, calculate_content_metrics

__all__ = [
    "TokenLevelMetrics",
    "calculate_token_level_metrics",
    "ContentMetrics",
    "calculate_content_metrics",
]
