import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.price_service import PriceDataError
from app.core.fundamentals_service import FundamentalsDataError
from app.providers.yahoo_client import YahooClientError, YahooSymbolNotFoundError
from app.utils.ticker import InvalidTickerError
import app.api.routes.eval as eval_route


client = TestClient(app)


@pytest.fixture(autouse=True)
def override_eval(monkeypatch):
    async def fake_evaluate_all(symbol: str):
        if symbol == "AAPL":
            return {
                "price": {
                    "price.current": 100.0,
                    "price.change_1d_pct": 1.0,
                    "price.change_1w_pct": 2.0,
                },
                "fundamentals": {
                    "fundamentals.pe_ttm": 20.0,
                },
                "technical": {
                    "technical.above_200d": True,
                    "technical.rsi_14d": 50.0,
                },
            }
        if symbol == "BAD":
            raise InvalidTickerError("bad ticker")
        if symbol == "MISS":
            raise YahooSymbolNotFoundError("missing")
        if symbol == "BROKE":
            raise YahooClientError("upstream")
        if symbol == "PERR":
            raise PriceDataError("price problem")
        if symbol == "FERR":
            raise FundamentalsDataError("fundamentals problem")
        raise Exception("unexpected test symbol")

    monkeypatch.setattr(eval_route, "evaluate_all", fake_evaluate_all)


def test_eval_endpoint_success():
    response = client.get("/eval/AAPL")
    assert response.status_code == 200

    body = response.json()
    assert body["ticker"] == "AAPL"
    assert body["metrics"]["price"]["price.current"] == 100.0
    assert body["metrics"]["technical"]["technical.above_200d"] is True


def test_eval_endpoint_invalid_format_returns_422():
    response = client.get("/eval/BAD")
    assert response.status_code == 422
    assert response.json()["detail"]["error"] == "INVALID_TICKER_FORMAT"


def test_eval_endpoint_not_found_returns_404():
    response = client.get("/eval/MISS")
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "TICKER_NOT_FOUND"


@pytest.mark.parametrize("symbol", ["BROKE", "PERR", "FERR"])
def test_eval_endpoint_upstream_errors_return_502(symbol: str):
    response = client.get(f"/eval/{symbol}")
    assert response.status_code == 502
    assert response.json()["detail"]["error"] == "YAHOO_CLIENT_ERROR"
