from typing import Dict, Any, Optional

from .base import BaseMetric
from app.core.price_service import PriceService
from app.providers.yahoo_client import YFinanceYahooClient

def get_price_service() -> PriceService:
    return PriceService(yahoo_client=YFinanceYahooClient())

class StockPriceMetric(BaseMetric):
    """Implements a metric to fetch the current stock price.

    Args:
        BaseMetric : Inherits from the BaseMetric class.
    """
    name = "price"
    
    def __init__(self, service: Optional[PriceService] = None) -> None:
        self.service = service or get_price_service()
    
    async def compute(self, ticker: str) -> Dict[str, Any]:
        """Fetch the current stock price for the given ticker.
        Args:
            ticker (str): Stock ticker symbol.
        Returns:
            Dict[str, Any]: A dictionary containing price metrics.
        """
        res = await self.service.get_price_for_symbol(ticker)
        return {
            "price.current": res.current,
            "price.change_1d_pct": res.change_1d_pct,
            "price.change_1w_pct": res.change_1w_pct,
        }