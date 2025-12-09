from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.utils.ticker import normalise_and_validate_ticker
from app.providers.yahoo_client import YahooClient, YahooSymbolNotFoundError, YahooClientError
from app.schemas.fundamentals import FundamentalsResponse

class FundamentalsDataError(Exception):
    """Custom exception for fundamentals data retrieval errors."""
    
def _latest_numeric(data: Dict[Any, Any]) -> Optional[float]:
    """
    Get the most recent numeric value from a data dictionary.

    Args:
        data (Dict[Any, Any]):  The data dictionary.

    Returns:
        Optional[float]: The most recent numeric value or None if not found.
    """
    if not isinstance(data, dict) or not data:
        return None
    try:
        latest_period = sorted(data.keys())[-1]
        return float(data[latest_period])
    except Exception:
        return None
    
    
@dataclass
class FundamentalsService:
    """
    Service for retrieving fundamentals data
    """
    yahoo_client: YahooClient
    
    async def get_fundamentals_for_symbol(self, raw_symbol: str) -> FundamentalsResponse:
        """
        Get fundamentals data for a symbol

        Args:
            raw_symbol (str): The raw symbol to get fundamentals data for.
        Returns:
            FundamentalsResponse: The fundamentals data response.
        """
        symbol = normalise_and_validate_ticker(raw_symbol)
        
        try:
            raw = await self.yahoo_client.fetch_fundamentals(symbol)
        except (YahooSymbolNotFoundError, YahooClientError):
            # Bubble up to the API
            raise
        
        info = raw.get("info", {}) or {}
        income = raw.get("income_statement", {}) or {}
        cashflow = raw.get("cashflow", {}) or {}
        
        market_cap = _safe_float(info.get("marketCap"))
        pe_ttm = _safe_float(info.get("trailingPE"))
        pe_forward = _safe_float(info.get("forwardPE"))
        dividend_yield = _percent_from_decimal(info.get("dividendYield"))
        
        free_cashflow = _latest_numeric(cashflow.get("Free Cash Flow", {}))
        fcf_yield = _ratio_percent(free_cashflow, market_cap)
        
        # Return on Invested Capital (ROIC)
        roic = _percent_from_decimal(info.get("returnOnInvestedCapital"))
        if roic is None:
            roic = _percent_from_decimal(info.get("returnOnEquity"))
        
        # 5 Year Revenue Growth
        revenue_growth_5y = _revenue_cagr_percent(income.get("Total Revenue", {}), years=5)
        
        return FundamentalsResponse(
            symbol=symbol,
            pe_ttm=pe_ttm,
            pe_forward=pe_forward,
            market_cap=market_cap,
            dividend_yield=dividend_yield,
            return_on_invested_capital=roic,
            fcf_yield=fcf_yield,
            revenue_growth_5y=revenue_growth_5y,
        )
        
def _safe_float(value: Any) -> Optional[float]:
    """
    Safely convert a value to float.

    Args:
        value (Any): The value to convert.

    Returns:
        Optional[float]: The float value or None if conversion fails.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
    
def _percent_from_decimal(value: Any) -> Optional[float]:
    """
    Convert a decimal value to percentage.

    Args:
        value (Any): The decimal value.

    Returns:
        Optional[float]: The percentage value or None if conversion fails.
    """
    decimal_value = _safe_float(value)
    if decimal_value is None:
        return None
    return decimal_value * 100.0

def _ratio_percent(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    """
    Calculate the ratio as a percentage.

    Args:
        numerator (Optional[float]): The numerator value.
        denominator (Optional[float]): The denominator value.

    Returns:
        Optional[float]: The ratio percentage or None if calculation fails.
    """
    if numerator is None or denominator is None or denominator == 0:
        return None
    return (numerator / denominator) * 100.0

def _revenue_cagr_percent(revenue_data: Dict[Any, Any], years: int = 5) -> Optional[float]:
    """
    Calculate the cagr for revenue over a number of years.

    Args:
        revenue_data (Dict[Any, Any]): The revenue data dictionary.
        years (int): The number of years for CAGR calculation.

    Returns:
        Optional[float]: The CAGR percentage or None if calculation fails.
    """
    if not revenue_data:
        return None
    try:
        periods = sorted(revenue_data.keys())
        start = float(revenue_data[periods[0]])
        end = float(revenue_data[periods[-1]])
    except Exception:
        return None
    
    if start <= 0 or end <= 0:
        return None
    
    span_years = max(1, min(years, len(periods) - 1))
    
    # Compound Annual Growth Rate calculation
    cagr = (end / start) ** (1 / span_years) - 1
    return cagr * 100.0
    
        
    
    
