import pytest
from datetime import datetime, timedelta

from app.core.price_service import PriceService, PriceDataError
from app.providers.yahoo_client import YahooClientError, YahooSymbolNotFoundError
from app.utils.ticker import InvalidTickerError
from app.schemas.price import PriceResponse

class FakeYahooClient:
    """
    Fake Yahoo client for testing PriceService.
    Behavior is driven by the symbol passed to history.
    """

    async def fetch_daily_history(self, symbol: str, days: int):
        if symbol == "AAPL":
            # Return 7 days of increasing prices
            base = 100.0
            now = datetime.utcnow()
            history = []
            for i in range(7):
                history.append({
                    "date": now - timedelta(days=7 - i),
                    "close": base + i,
                })
            return history

        if symbol == "MISS":
            raise YahooSymbolNotFoundError("missing")

        if symbol == "BROKE":
            raise YahooClientError("upstream error")

        if symbol == "SHORT":
            # Not enough data (< 2 points)
            return [
                {
                    "date": datetime.utcnow(),
                    "close": 150.0
                }
            ]

        # Default: behave like AAPL
        return await self.fetch_daily_history("AAPL", days)

    # Required by protocol but not used in these tests
    async def fetch_quote(self, symbol: str):
        return {"symbol": symbol, "regularMarketPrice": 123.0}


@pytest.mark.asyncio
async def test_price_service_success():
    service = PriceService(yahoo_client=FakeYahooClient())

    result = await service.get_price_for_symbol("AAPL")

    assert isinstance(result, PriceResponse)
    assert result.symbol == "AAPL"
    assert result.current == 100.0 + 6
    assert result.change_1d_pct != 0
    assert result.change_1w_pct != 0


@pytest.mark.asyncio
async def test_price_service_invalid_ticker():
    service = PriceService(yahoo_client=FakeYahooClient())

    # "$$$" is invalid format
    with pytest.raises(InvalidTickerError):
        await service.get_price_for_symbol("$$$")


@pytest.mark.asyncio
async def test_price_service_missing_symbol():
    service = PriceService(yahoo_client=FakeYahooClient())

    with pytest.raises(YahooSymbolNotFoundError):
        await service.get_price_for_symbol("MISS")


@pytest.mark.asyncio
async def test_price_service_upstream_error():
    service = PriceService(yahoo_client=FakeYahooClient())

    with pytest.raises(YahooClientError):
        await service.get_price_for_symbol("BROKE")


@pytest.mark.asyncio
async def test_price_service_not_enough_history():
    service = PriceService(yahoo_client=FakeYahooClient())

    with pytest.raises(PriceDataError):
        await service.get_price_for_symbol("SHORT")