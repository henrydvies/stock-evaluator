from .base import BaseMetric
from app.core.fundamentals_service import FundamentalsService

class StockFundamentalsMetric(BaseMetric):
    """Implements a metric to fetch stock fundamentals.

    Args:
        BaseMetric : Inherits from the BaseMetric class.
    """
    name = "stock_fundamentals"
    
    async def compute(self, ticker: str):
        """Fetch the stock fundamentals for the given ticker.
        Args:
            ticker (str): Stock ticker symbol.
        Returns:
            FundamentalsResponse: The fundamentals data response.
        """
        return await FundamentalsService().get_fundamentals_for_symbol(ticker)