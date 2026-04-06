import pytest

from app.core.technical_service import TechnicalService
from app.providers.yahoo_client import YahooSymbolNotFoundError, YahooClientError
from app.utils.ticker import InvalidTickerError
from app.schemas.technical import TechnicalResponse


class FakeYahooClient:
	async def fetch_technical(self, symbol: str):
		if symbol == "AAPL":
			return {
				"sma_50d": 180.5,
				"sma_200d": 165.0,
				"above_200d": True,
				"rsi_14d": 61.2,
				"volatility_30": 1.8,
			}
		if symbol == "MISS":
			raise YahooSymbolNotFoundError("not found")
		if symbol == "BROKE":
			raise YahooClientError("upstream")
		if symbol == "NANVA":
			return {
				"sma_50d": float("nan"),
				"sma_200d": float("inf"),
				"above_200d": False,
				"rsi_14d": None,
				"volatility_30": "bad",
			}
		return {}


@pytest.mark.asyncio
async def test_technical_service_success():
	service = TechnicalService(yahoo_client=FakeYahooClient())

	res = await service.get_technical_for_symbol("AAPL")

	assert isinstance(res, TechnicalResponse)
	assert res.symbol == "AAPL"
	assert res.sma_50d == 180.5
	assert res.sma_200d == 165.0
	assert res.above_200d is True
	assert res.rsi_14d == 61.2
	assert res.volatility_30 == 1.8


@pytest.mark.asyncio
async def test_technical_service_invalid_ticker():
	service = TechnicalService(yahoo_client=FakeYahooClient())

	with pytest.raises(InvalidTickerError):
		await service.get_technical_for_symbol("$$$")


@pytest.mark.asyncio
async def test_technical_service_not_found():
	service = TechnicalService(yahoo_client=FakeYahooClient())

	with pytest.raises(YahooSymbolNotFoundError):
		await service.get_technical_for_symbol("MISS")


@pytest.mark.asyncio
async def test_technical_service_upstream_error():
	service = TechnicalService(yahoo_client=FakeYahooClient())

	with pytest.raises(YahooClientError):
		await service.get_technical_for_symbol("BROKE")


@pytest.mark.asyncio
async def test_technical_service_filters_non_finite_values():
	service = TechnicalService(yahoo_client=FakeYahooClient())

	res = await service.get_technical_for_symbol("NANVA")

	assert res.symbol == "NANVA"
	assert res.sma_50d is None
	assert res.sma_200d is None
	assert res.above_200d is False
	assert res.rsi_14d is None
	assert res.volatility_30 is None