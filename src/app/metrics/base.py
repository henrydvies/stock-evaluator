from abc import ABC, abstractmethod
from typing import Any

class BaseMetric(ABC):
    """Base class for all metrics.

    Args:
        ABC : Abstract Base Class for defining abstract methods.
    """
    
    name: str
    
    @abstractmethod
    async def compute(self, ticker: str) -> Any:
        """Compute the metric for a given ticker.

        Args:
            ticker (str): Stock ticker symbol."""
        pass
    