from .base import BaseMetric
from typing import Dict, Any, Optional

from app.core.fundamentals_service import FundamentalsService
from app.providers.yahoo_client import YFinanceYahooClient

def get_fundamentals_service() -> FundamentalsService:
    return FundamentalsService(yahoo_client=YFinanceYahooClient())

class StockFundamentalsMetric(BaseMetric):
    """Implements a metric to fetch stock fundamentals.

    Args:
        BaseMetric : Inherits from the BaseMetric class.
    """
    name = "fundamentals"
    
    def __init__(self, service: Optional[FundamentalsService] = None) -> None:
        self.service = service or get_fundamentals_service()
    
    async def compute(self, ticker: str) -> Dict[str, Any]:
        """Fetch the stock fundamentals for the given ticker.
        Args:
            ticker (str): Stock ticker symbol.
        Returns:
            Dict[str, Any]: A dictionary containing fundamentals metrics.
        """
        res = await self.service.get_fundamentals_for_symbol(ticker)
        return {
            "fundamentals.pe_ttm": res.pe_ttm,
            "fundamentals.pe_forward": res.pe_forward,
            "fundamentals.market_cap": res.market_cap,
            "fundamentals.dividend_yield": res.dividend_yield,
            "fundamentals.return_on_invested_capital": res.return_on_invested_capital,
            "fundamentals.fcf_yield": res.fcf_yield,
            "fundamentals.revenue_growth_5y": res.revenue_growth_5y,
        }