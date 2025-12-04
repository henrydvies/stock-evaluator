from dataclasses import dataclass
from app.utils.ticker import normalise_and_validate_ticker
from app.providers.yahoo_client import YahooClient, YahooClientError, ticker_exists

class TickerNotFoundError(Exception):
    """
    Raised when a ticker symbol is not found in the data source.
    """
    pass

@dataclass
class TickerValidationService:
    """
    Service for validating ticker symbols using a YahooClient.
    """
    yahoo_client: YahooClient
    
    async def validate_ticker(self, raw_ticker: str) -> str:
        """
        Validate a ticker symbol by normalising it and checking its existence.

        Args:
            raw_ticker (str): The raw ticker symbol input.
        """
        symbol = normalise_and_validate_ticker(raw_ticker)
        
        exists = await ticker_exists(symbol, self.yahoo_client)
        if not exists:
            raise TickerNotFoundError(f"Ticker symbol '{symbol}' not found.")
        
        return symbol