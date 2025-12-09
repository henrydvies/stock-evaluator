import pytest

from app.core.fundamentals_service import FundamentalsService
from app.providers.yahoo_client import YahooSymbolNotFoundError, YahooClientError
from app.utils.ticker import InvalidTickerError


class FakeYahooClient:
    async def fetch_fundamentals(self, symbol: str):
        if symbol == "AAPL":
            return {
                "info": {
                    "marketCap": 1_000.0,
                    "trailingPE": 25.0,
                    "forwardPE": 20.0,
                    "dividendYield": 1,            # 1%
                    "returnOnInvestedCapital": 0.15,  # 15%
                },
                "income_statement": {
                    "Total Revenue": {
                        "2019": 100.0,
                        "2024": 200.0,
                    }
                },
                "cashflow": {
                    "Free Cash Flow": {
                        "2024": 50.0,
                    }
                },
            }
        if symbol == "MISS":
            raise YahooSymbolNotFoundError("not found")
        if symbol == "BROKE":
            raise YahooClientError("upstream")
        if symbol == "NANRE":
            return {
                "info": {},
                "income_statement": {"Total Revenue": {"2024": float("nan")}},
                "cashflow": {},
            }
        return {"info": {}, "income_statement": {}, "cashflow": {}}


@pytest.mark.asyncio
async def test_fundamentals_service_success():
    service = FundamentalsService(yahoo_client=FakeYahooClient())

    res = await service.get_fundamentals_for_symbol("AAPL")

    assert res.symbol == "AAPL"
    assert res.pe_ttm == 25.0
    assert res.pe_forward == 20.0
    assert res.market_cap == 1_000.0
    assert res.dividend_yield == 1.0
    assert res.return_on_invested_capital == 15.0
    assert res.fcf_yield == 5.0
    # Revenue doubled over the span -> 100% CAGR with span_years=1
    assert res.revenue_growth_5y == 100.0


@pytest.mark.asyncio
async def test_fundamentals_service_invalid_ticker():
    service = FundamentalsService(yahoo_client=FakeYahooClient())

    with pytest.raises(InvalidTickerError):
        await service.get_fundamentals_for_symbol("$$$")


@pytest.mark.asyncio
async def test_fundamentals_service_not_found():
    service = FundamentalsService(yahoo_client=FakeYahooClient())

    with pytest.raises(YahooSymbolNotFoundError):
        await service.get_fundamentals_for_symbol("MISS")


@pytest.mark.asyncio
async def test_fundamentals_service_upstream_error():
    service = FundamentalsService(yahoo_client=FakeYahooClient())

    with pytest.raises(YahooClientError):
        await service.get_fundamentals_for_symbol("BROKE")


@pytest.mark.asyncio
async def test_fundamentals_service_filters_nan():
    service = FundamentalsService(yahoo_client=FakeYahooClient())

    res = await service.get_fundamentals_for_symbol("NANRE")

    assert res.revenue_growth_5y is None
