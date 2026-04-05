import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.technical import get_technical_service
from app.schemas.technical import TechnicalResponse
from app.providers.yahoo_client import YahooClientError, YahooSymbolNotFoundError
from app.utils.ticker import InvalidTickerError


class FakeTechnicalService:
    async def get_technical_for_symbol(self, symbol: str) -> TechnicalResponse:
        if symbol == "AAPL":
            return TechnicalResponse(
                symbol="AAPL",
                sma_50d=250.0,
                sma_200d=230.0,
                above_200d=True,
                rsi_14d=55.0,
                volatility_30=2.1,
            )
        if symbol == "BAD":
            raise InvalidTickerError("bad ticker")
        if symbol == "MISS":
            raise YahooSymbolNotFoundError("missing")
        if symbol == "BROKE":
            raise YahooClientError("upstream")
        raise Exception("unexpected test symbol")


@pytest.fixture(autouse=True)
def override_technical_service():
    app.dependency_overrides[get_technical_service] = lambda: FakeTechnicalService()
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


def test_technical_endpoint_success():
    response = client.get("/technical/AAPL")
    assert response.status_code == 200

    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["sma_50d"] == 250.0
    assert body["above_200d"] is True


def test_technical_endpoint_invalid_format_returns_422():
    response = client.get("/technical/BAD")
    assert response.status_code == 422

    body = response.json()
    assert body["detail"]["error"] == "INVALID_TICKER_FORMAT"


def test_technical_endpoint_not_found_returns_404():
    response = client.get("/technical/MISS")
    assert response.status_code == 404

    body = response.json()
    assert body["detail"]["error"] == "TICKER_NOT_FOUND"


def test_technical_endpoint_upstream_error_returns_502():
    response = client.get("/technical/BROKE")
    assert response.status_code == 502

    body = response.json()
    assert body["detail"]["error"] == "YAHOO_CLIENT_ERROR"
