import pytest

from app.providers.yahoo_client import ticker_exists, YahooSymbolNotFoundError, YahooClientError


class FakeYahooClient:
    async def fetch_quote(self, symbol: str):
        if symbol == "AAPL":
            return {"symbol": "AAPL"}
        if symbol == "MISS":
            raise YahooSymbolNotFoundError("not found")
        raise RuntimeError("boom")


@pytest.mark.asyncio
async def test_ticker_exists_true_when_quote_found():
    assert await ticker_exists("AAPL", FakeYahooClient()) is True


@pytest.mark.asyncio
async def test_ticker_exists_false_when_symbol_missing():
    assert await ticker_exists("MISS", FakeYahooClient()) is False


@pytest.mark.asyncio
async def test_ticker_exists_wraps_unexpected_errors():
    with pytest.raises(YahooClientError):
        await ticker_exists("BROKE", FakeYahooClient())
