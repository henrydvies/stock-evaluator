import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.fundamentals import get_fundamentals_service
from app.schemas.fundamentals import FundamentalsResponse
from app.utils.ticker import InvalidTickerError
from app.providers.yahoo_client import YahooSymbolNotFoundError, YahooClientError


class FakeFundamentalsService:
    async def get_fundamentals_for_symbol(self, symbol: str) -> FundamentalsResponse:
        if symbol == "AAPL":
            return FundamentalsResponse(
                symbol="AAPL",
                pe_ttm=25.0,
                pe_forward=20.0,
                market_cap=1_000.0,
                dividend_yield=1.0,
                return_on_invested_capital=15.0,
                fcf_yield=5.0,
                revenue_growth_5y=100.0,
            )
        if symbol == "BAD":
            raise InvalidTickerError("bad ticker")
        if symbol == "MISS":
            raise YahooSymbolNotFoundError("not found")
        if symbol == "BROKE":
            raise YahooClientError("upstream")
        raise Exception("unexpected test symbol")


@pytest.fixture(autouse=True)
def override_fundamentals_dependency():
    app.dependency_overrides[get_fundamentals_service] = lambda: FakeFundamentalsService()
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


def test_fundamentals_endpoint_success():
    resp = client.get("/fundamentals/AAPL")
    assert resp.status_code == 200

    body = resp.json()
    assert body["symbol"] == "AAPL"
    assert body["pe_ttm"] == 25.0
    assert body["fcf_yield"] == 5.0


def test_fundamentals_endpoint_invalid_format_returns_422():
    resp = client.get("/fundamentals/BAD")
    assert resp.status_code == 422
    assert resp.json()["detail"]["error"] == "INVALID_TICKER_FORMAT"


def test_fundamentals_endpoint_not_found_returns_404():
    resp = client.get("/fundamentals/MISS")
    assert resp.status_code == 404
    assert resp.json()["detail"]["error"] == "TICKER_NOT_FOUND"


def test_fundamentals_endpoint_upstream_error_returns_502():
    resp = client.get("/fundamentals/BROKE")
    assert resp.status_code == 502
    assert resp.json()["detail"]["error"] == "YAHOO_CLIENT_ERROR"
