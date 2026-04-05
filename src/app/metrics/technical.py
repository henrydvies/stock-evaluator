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
        res = await self.service.get_technical_for_symbol(ticker)
        return {
            "technical.sma_50d": res.sma_50d,
            "technical.sma_200d": res.sma_200d,
            "technical.above_200d": res.above_200d,
            "technical.rsi_14d": res.rsi_14d,
            "technical.volatility_30": res.volatility_30,
        }
    
    