import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.price import get_price_service
from app.schemas.price import PriceResponse
from app.providers.yahoo_client import YahooClientError, YahooSymbolNotFoundError
from app.utils.ticker import InvalidTickerError


#
# Fake service for dependency override
#
class FakePriceService:
    async def get_price_for_symbol(self, symbol: str) -> PriceResponse:
        if symbol == "AAPL":
            return PriceResponse(
                symbol="AAPL",
                current=150.0,
                change_1d_pct=1.23,
                change_1w_pct=3.45,
            )

        if symbol == "BAD":
            raise InvalidTickerError("bad ticker")

        if symbol == "MISS":
            raise YahooSymbolNotFoundError("missing")

        if symbol == "BROKE":
            raise YahooClientError("upstream")

        raise Exception("unexpected test symbol")


@pytest.fixture(autouse=True)
def override_price_service():
    app.dependency_overrides[get_price_service] = lambda: FakePriceService()
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


#
# Tests
#

def test_price_endpoint_success():
    response = client.get("/price/AAPL")
    assert response.status_code == 200

    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["current"] == 150.0
    assert body["change_1d_pct"] == 1.23


def test_price_endpoint_invalid_format_returns_422():
    response = client.get("/price/BAD")
    assert response.status_code == 422

    body = response.json()
    assert body["detail"]["error"] == "INVALID_TICKER_FORMAT"


def test_price_endpoint_not_found_returns_404():
    response = client.get("/price/MISS")
    assert response.status_code == 404

    body = response.json()
    assert body["detail"]["error"] == "TICKER_NOT_FOUND"


def test_price_endpoint_upstream_error_returns_502():
    response = client.get("/price/BROKE")
    assert response.status_code == 502

    body = response.json()
    assert body["detail"]["error"] == "YAHOO_CLIENT_ERROR"
