from dataclasses import dataclass
from typing import Protocol, Any, Dict, List

import asyncio
import yfinance as yf
import pandas as pd 

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
        Returns:
            Dict[str, Any]: Quote data.
        """
        ...
    
    async def fetch_daily_history(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """
        Fetch daily historical data for a given stock symbol.

        Args:
            symbol (str): Stock ticker symbol.
            days (int): Number of days of history to fetch.
        Returns:
            List[Dict[str, Any]]: Daily historical data.
        """
        ...
        
    async def fetch_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch raw fundamentals for a given stock symbol.

        Args:
            symbol (str): Stock ticker symbol.

        Returns:
            Dict[str, Any]: Raw fundamentals data.
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
    
    async def fetch_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch raw fundamentals for a given stock symbol using yfinance.

        Args:
            symbol (str): Stock ticker symbol.
        """
        
        def _get_fundamentals_sync() -> Dict[str, Any]:
            ticker = yf.Ticker(symbol)
            
            info = ticker.info
            if info is None or not info:
                hist = ticker.history(period="1d")
                if hist.empty:
                    raise YahooSymbolNotFoundError(f"Symbol '{symbol}' not found.")
                
            # Cpmvert to dict
            info_dict: Dict[str, Any] = dict(info) if info else {}
            
            # Get the income statement
            income_stmt_df: pd.DataFrame = getattr(ticker, "income_stmt", None)
            if income_stmt_df is None or income_stmt_df.empty:
                income_stmt: Dict[str, Any] = {}
            else:
                income_stmt = income_stmt_df.to_dict(orient="index")
            
            # Get the balance sheet
            balance_sheet_df: pd.DataFrame = getattr(ticker, "balance_sheet", None)
            if balance_sheet_df is None or balance_sheet_df.empty:
                balance_sheet: Dict[str, Any] = {}
            else:
                balance_sheet = balance_sheet_df.to_dict(orient="index")
            
            # Get the cashflow statement
            cashflow_df: pd.DataFrame = getattr(ticker, "cashflow", None)
            if cashflow_df is None or cashflow_df.empty:
                cashflow: Dict[str, Any] = {}
            else:
                cashflow = cashflow_df.to_dict(orient="index")

            if not info_dict and not income_stmt and not balance_sheet and not cashflow:
                raise YahooSymbolNotFoundError(f"Fundamentals for '{symbol}' not found.")

            return {
                "symbol": symbol,
                "info": info_dict,
                "income_statement": income_stmt,
                "balance_sheet": balance_sheet,
                "cashflow": cashflow,
            }
        try:
            return await asyncio.to_thread(_get_fundamentals_sync)
        except YahooSymbolNotFoundError:
            raise
        except Exception as e:
            raise YahooClientError(f"Error fetching fundamentals for '{symbol}': {e}") from e
            
        
        
        
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