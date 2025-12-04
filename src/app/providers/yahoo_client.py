from dataclasses import dataclass
from typing import Protocol, Any, Dict, List

import asyncio
import yfinance as yf

class YahooClientError(Exception):
    """"""
    
class YahooSymbolNotFoundError(YahooClientError):
    """"""
    
class YahooClient(Protocol):
    """
    Protocol for Yahoo Finance client implementations.
    """
    async def fetch_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch quote data for a given stock symbol.

        Args:
            symbol (str): Stock ticker symbol.
        """
        ...
    
    async def fetch_daily_history(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """
        Fetch daily historical data for a given stock symbol.

        Args:
            symbol (str): Stock ticker symbol.
            days (int): Number of days of history to fetch.
        """
        ...

@dataclass
class YFinanceYahooClient:
    """
    """
    async def fetch_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch quote data for a given stock symbol using yfinance.

        Args:
            symbol (str): Stock ticker symbol.
        Returns:
            Dict[str, Any]: Quote data.
        """
        
        def _get_quote_sync() -> Dict[str, Any]:
            ticker = yf.Ticker(symbol)
            
            info = ticker.info
            
            if info is None:
                # Fallback
                hist = ticker.history(period="1d")
                if hist.empty:
                    raise YahooSymbolNotFoundError(f"Symbol '{symbol}' not found.")

                last_row = hist.iloc[-1]
                
                return {
                    "symbol": symbol,
                    "regularMarketPrice": float(last_row["Close"]),
                }
            data = dict(info)
            
            if not data:
                raise YahooSymbolNotFoundError(f"Symbol '{symbol}' not found.")
            
            # Check symbol in the info
            data.setdefault("symbol", symbol)
            return data
        
        try:
            return await asyncio.to_thread(_get_quote_sync)
        except YahooSymbolNotFoundError:
            raise
        except Exception as e:
            raise YahooClientError(f"Error fetching quote for '{symbol}': {e}") from e      
        
    async def fetch_daily_history(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """
        Fetch daily close prices for the 'days' days.

        Args:
            symbol (str): Stock ticker symbol.
            days (int): Number of days of history to fetch.

        Returns:
            List[Dict[str, Any]]: Daily historical data.
        """
        import pandas as pd 
        
        def _get_history_sync() -> List[Dict[str, Any]]:
            ticker = yf.Ticker(symbol)
            
            # Fetch history with a bit of buffer
            hist = ticker.history(period=f"{days + 2}d", interval="1d")
            
            if hist.empty:
                raise YahooSymbolNotFoundError(f"History for '{symbol}' not found.")
            
            # Build a list of {date, close} sorted by date
            records: List[Dict[str, Any]] = []
            for ts, row in hist.iterrows():
                records.append({
                    "date": ts.to_pydatetime(),
                    "close": float(row["Close"]),
                    }
                )
            
            # Sort by date
            records.sort(key=lambda x: x["date"])
            
            return records[-days:]
        try:
            return await asyncio.to_thread(_get_history_sync)
        except YahooSymbolNotFoundError:
            raise
        except Exception as e:
            raise YahooClientError(f"Error fetching history for '{symbol}': {e}") from e
        
        
        
async def ticker_exists(symbol: str, client: YahooClient) -> bool:
    """
    Check if a ticker symbol exists using the provided YahooClient.

    Args:
        symbol (str): Stock ticker symbol.
        client (YahooClient): An instance of a YahooClient implementation.
    Returns:
        bool: True if the ticker exists, False otherwise.
    """
    try:
        await client.fetch_quote(symbol)
        return True
    except YahooSymbolNotFoundError:
        return False
    except Exception as e:
        raise YahooClientError(f"Error talking to Yahoo Finance: {e}") from e