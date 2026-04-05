import pytest

from app.metrics.price import StockPriceMetric
from app.metrics.fundamentals import StockFundamentalsMetric
from app.metrics.technical import StockTechnicalMetric
from app.schemas.price import PriceResponse
from app.schemas.fundamentals import FundamentalsResponse
from app.schemas.technical import TechnicalResponse
import app.metrics as metrics_module


class FakePriceService:
    async def get_price_for_symbol(self, symbol: str) -> PriceResponse:
        return PriceResponse(symbol=symbol, current=100.0, change_1d_pct=1.0, change_1w_pct=2.0)


class FakeFundamentalsService:
    async def get_fundamentals_for_symbol(self, symbol: str) -> FundamentalsResponse:
        return FundamentalsResponse(
            symbol=symbol,
            pe_ttm=20.0,
            pe_forward=18.0,
            market_cap=1_000.0,
            dividend_yield=1.2,
            return_on_invested_capital=10.0,
            fcf_yield=4.0,
            revenue_growth_5y=8.0,
        )


class FakeTechnicalService:
    async def get_technical_for_symbol(self, symbol: str) -> TechnicalResponse:
        return TechnicalResponse(
            symbol=symbol,
            sma_50d=150.0,
            sma_200d=140.0,
            above_200d=True,
            rsi_14d=52.0,
            volatility_30=2.3,
        )


@pytest.mark.asyncio
async def test_price_metric_compute_shape():
    metric = StockPriceMetric(service=FakePriceService())
    result = await metric.compute("AAPL")

    assert result["price.current"] == 100.0
    assert result["price.change_1d_pct"] == 1.0
    assert result["price.change_1w_pct"] == 2.0


@pytest.mark.asyncio
async def test_fundamentals_metric_compute_shape():
    metric = StockFundamentalsMetric(service=FakeFundamentalsService())
    result = await metric.compute("AAPL")

    assert result["fundamentals.pe_ttm"] == 20.0
    assert result["fundamentals.fcf_yield"] == 4.0


@pytest.mark.asyncio
async def test_technical_metric_compute_shape():
    metric = StockTechnicalMetric(service=FakeTechnicalService())
    result = await metric.compute("AAPL")

    assert result["technical.sma_50d"] == 150.0
    assert result["technical.above_200d"] is True


@pytest.mark.asyncio
async def test_evaluate_all_aggregates_metric_results(monkeypatch):
    class MetricOne:
        name = "one"

        async def compute(self, ticker: str):
            return {"k1": 1.0}

    class MetricTwo:
        name = "two"

        async def compute(self, ticker: str):
            return {"k2": 2.0}

    monkeypatch.setattr(metrics_module, "_METRICS", [MetricOne(), MetricTwo()])

    result = await metrics_module.evaluate_all("AAPL")
    assert result == {
        "one": {"k1": 1.0},
        "two": {"k2": 2.0},
    }
