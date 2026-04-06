from typing import Optional
from pydantic import BaseModel, Field

class TechnicalResponse(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol.")
    sma_50d: Optional[float] = Field(None, description="Simple Moving Average over the past 50 days.")
    sma_200d: Optional[float] = Field(None, description="Simple Moving Average over the past 200 days.")
    above_200d: Optional[bool] = Field(None, description="Indicates if the current price is above the 200-day SMA.")
    rsi_14d: Optional[float] = Field(None, description="Relative Strength Index over the past 14 days.")
    volatility_30: Optional[float] = Field(None, description="Standard deviation of the last 30 changes in closing prices.")
