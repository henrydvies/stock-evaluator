from typing import Optional
from pydantic import BaseModel, Field

class FundamentalsResponse(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol.")
    pe_ttm: Optional[float] = Field(None, description="Trailing Twelve Months Price to Earnings ratio.")
    pe_forward: Optional[float] = Field(None, description="Forward Price to Earnings ratio.")
    market_cap: Optional[float] = Field(None, description="Market Cap.")
    dividend_yield: Optional[float] = Field(None, description="Dividend Yield.")
    return_on_invested_capital: Optional[float] = Field(None, description="Return on Invested Capital.")
    fcf_yield: Optional[float] = Field(None, description="Free Cash Flow Yield.")
    revenue_growth_5y: Optional[float] = Field(None, description="5 Year Revenue Growth Percentage.")
