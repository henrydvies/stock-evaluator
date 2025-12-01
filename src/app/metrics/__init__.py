from typing import Dict, Any, List

from .base import BaseMetric
from .price import StockPriceMetric

# List of all available metrics
_METRICS: List[BaseMetric] = [
    StockPriceMetric(),
]

async def evaluate_all(ticker: str) -> Dict[str, Any]:
    """Evaluate all metrics for a given ticker.

    Args:
        ticker (str): Stock ticker symbol."""
    
    results: Dict[str, Any] = {}
    
    # Compute each metric and store the results
    for metric in _METRICS:
        value = await metric.compute(ticker)
        results[metric.name] = value
    
    return results