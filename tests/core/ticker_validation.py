import pytest

from app.core.ticker_validation import (
    TickerValidationService,
    TickerNotFoundError,
)

from app.providers.yahoo_client import (
    YahooClientError,
    YahooSymbolNotFoundError,
)
from app.utils.ticker import InvalidTickerError

class MockYahooClient:
    """
    Fake Yahoo Client for testing TickerValidation service
    """
    async def fetch_quote(self, symbol: str):
        if symbol == "AAPL":
            return {"symbol": "AAPL", "price": 150.0}
        if symbol == "MISSING":
            # Simulate symbol not found
            raise YahooSymbolNotFoundError("No data for MISSING")
        if symbol == "BROEKN":
            # Simulate other Yahoo client error
            raise YahooClientError("Yahoo service error")

        # Default mock response
        return {"symbol": symbol, "price": 100.0}

@pytest.mark.asyncio
async def test_validate_ticker_success():
    service = TickerValidationService(yahoo_client=MockYahooClient())
    
    symbol = await service.validate_ticker(" aapl ")
    assert symbol == "AAPL"
    
@pytest.mark.asyncio
async def test_validate_ticker_invalid_format():
    service = TickerValidationService(yahoo_client=MockYahooClient())

    with pytest.raises(InvalidTickerError):
        await service.validate_ticker("$$$")


@pytest.mark.asyncio
async def test_validate_ticker_not_found():
    service = TickerValidationService(yahoo_client=MockYahooClient())

    with pytest.raises(TickerNotFoundError):
        await service.validate_ticker("MISSING")


@pytest.mark.asyncio
async def test_validate_ticker_upstream_error():
    service = TickerValidationService(yahoo_client=MockYahooClient())

    with pytest.raises(YahooClientError):
        await service.validate_ticker("BROKEN")
