import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import tickers
from app.core.ticker_validation import TickerNotFoundError
from app.utils.ticker import InvalidTickerError
from app.providers.yahoo_client import YahooClientError


class FakeTickerValidationService:
    """
    Fake service to simulate different outcomes for the endpoint.
    """

    async def validate_ticker(self, raw_symbol: str) -> str:
        if raw_symbol == "AAPL":
            return "AAPL"
        if raw_symbol == "BAD":
            raise InvalidTickerError("Ticker must be 1–5 uppercase letters, optional '.XX' suffix.")
        if raw_symbol == "MISSING":
            raise TickerNotFoundError("Ticker 'MISSING' not found on Yahoo Finance.")
        if raw_symbol == "UPSTREAM":
            raise YahooClientError("Failed to talk to Yahoo.")
        # default: treat as valid
        return raw_symbol.upper()


@pytest.fixture(autouse=True)
def override_ticker_validation_dependency():
    """
    Override dependency for all tests in this module.
    """
    app.dependency_overrides[tickers.get_ticker_validation_service] = (
        lambda: FakeTickerValidationService()
    )
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


def test_validate_ticker_success():
    response = client.get("/tickers/AAPL/validate")
    assert response.status_code == 200

    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["valid"] is True


def test_validate_ticker_invalid_format_returns_422():
    response = client.get("/tickers/BAD/validate")
    assert response.status_code == 422

    body = response.json()
    assert body["detail"]["error"] == "INVALID_TICKER_FORMAT"


def test_validate_ticker_not_found_returns_404():
    response = client.get("/tickers/MISSING/validate")
    assert response.status_code == 404

    body = response.json()
    assert body["detail"]["error"] == "TICKER_NOT_FOUND"


def test_validate_ticker_upstream_error_returns_502():
    response = client.get("/tickers/UPSTREAM/validate")
    assert response.status_code == 502

    body = response.json()
    assert body["detail"]["error"] == "YAHOO_CLIENT_ERROR"