from dataclasses import dataclass
from typing import Any, Dict

from app.providers.yahoo_client import YahooClient, YahooSymbolNotFoundError, YahooClientError
from app.schemas.technical import TechnicalResponse
from app.utils.ticker import normalise_and_validate_ticker
from app.core.utils.service_helpers import _safe_float

@dataclass
class TechnicalService:
    """
    Service for fetching technical data.
    """
    yahoo_client: YahooClient
    
    async def get_technical_for_symbol(self, raw_symbol: str) -> TechnicalResponse:
        """
        Get technical data for a symbol.

        Args:
            raw_symbol (str): The raw symbol to get technical data for.
        Returns:
            TechnicalResponse: The technical data response.
        """
        symbol = normalise_and_validate_ticker(raw_symbol)
        
        try:
            raw = await self.yahoo_client.fetch_technical(symbol)
        except (YahooSymbolNotFoundError, YahooClientError):
            # Bubble up to the API
            raise
        
        return TechnicalResponse(
            symbol=symbol,
            sma_50d=_safe_float(raw.get("sma_50d")),
            sma_200d=_safe_float(raw.get("sma_200d")),
            above_200d=raw.get("above_200d"),
            rsi_14d=_safe_float(raw.get("rsi_14d")),
            volatility_30=_safe_float(raw.get("volatility_30"))
        )