from .base import BaseMetric
from typing import Dict, Any, Optional

from app.core.technical_service import TechnicalService
from app.providers.yahoo_client import YFinanceYahooClient

def get_technical_service() -> TechnicalService:
    return TechnicalService(yahoo_client=YFinanceYahooClient())

class StockTechnicalMetric(BaseMetric):
    """Implements a metric to fetch stock technical indicators.

    Args:
        BaseMetric : Inherits from the BaseMetric class.
    """
    name = "technical"
    
    def __init__(self, service: Optional[TechnicalService] = None) -> None:
        self.service = service or get_technical_service()
    
    async def compute(self, ticker: str) -> Dict[str, Any]:
        """Fetch the stock technical indicators for the given ticker.
        Args:
            ticker (str): Stock ticker symbol.
        Returns:
            Dict[str, Any]: Dictionary of technical indicators.
        """
        return await self.service.get_technical_for_symbol(ticker)
    
    