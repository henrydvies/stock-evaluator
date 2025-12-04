from pydantic import BaseModel, Field

class PriceResponse(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol.")
    current: float = Field(..., description="Current stock price.")
    change_1d_pct: float = Field(..., description="Percentage change in price over the last day.")
    change_1w_pct: float = Field(..., description="Percentage change in price over the last 7 days.")