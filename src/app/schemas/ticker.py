from pydantic import BaseModel, Field
from typing import Optional

class TickerValidationResponse(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol")
    valid: bool = Field(..., description="Indicates if the ticker symbol is valid")
    
class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional details about the error")