from dataclasses import dataclass
from typing import List, Dict, Any

from app.utils.ticker import normalise_and_validate_ticker, InvalidTickerError
from app.providers.yahoo_client import YahooClient, YahooSymbolNotFoundError, YahooClientError
from app.schemas.price import PriceResponse

class PriceDataError(Exception):
    """Custom exception for price data retrieval errors."""
    
def _pct_change(current: float, previous: float) -> float:
    """
    Return the percentage change between current and previous values.

    Args:
        current (float): Current value.
        previous (float): Previous value.

    Returns:
        float: Percentage change.
    """
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100.0

@dataclass
class PriceService:
    """
    Service for retrieving price data
    """
    yahoo_client: YahooClient
    
    async def get_price_for_symbol(self, raw_symbol: str) -> PriceResponse:
        """
        Get price data for a symbol

        Args:
            raw_symbol (str): The raw symbol to get price data for.

        Returns:
            PriceResponse: The price data response.
        """
        symbol = normalise_and_validate_ticker(raw_symbol)
        
        try:
            history: List[Dict[str, Any]] = await self.yahoo_client.fetch_daily_history(symbol, days=7)
        except (YahooSymbolNotFoundError, YahooClientError):
            # Bubble up to the API
            raise
        
        if len(history) < 2:
            raise PriceDataError(f"Not enough price data for symbol '{symbol}'.")
        
        # History is oldest to newest
        latest = history[-1]["close"]
        prev_close = history[-2]["close"]
        week_ago_close = history[0]["close"]
        
        current = float(latest)
        change_1d_pct = _pct_change(current, float(prev_close))
        change_7d_pct = _pct_change(current, float(week_ago_close))
        
        return PriceResponse(
            symbol=symbol,
            current=current,
            change_1d_pct=change_1d_pct,
            change_7d_pct=change_7d_pct,
        )
        
        