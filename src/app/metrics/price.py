from .base import BaseMetric
from app.providers.market import get_current_price

class StockPriceMetric(BaseMetric):
    """Implements a metric to fetch the current stock price.

    Args:
        BaseMetric : Inherits from the BaseMetric class.
    """
    name = "stock_price"
    
    async def compute(self, ticker: str):
        """Fetch the current stock price for the given ticker.
        Args:
            ticker (str): Stock ticker symbol.
        """
        return await get_current_price(ticker)