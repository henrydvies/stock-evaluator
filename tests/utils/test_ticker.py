import pytest

from app.utils.ticker import (
    normalise_and_validate_ticker,
    InvalidTickerError,
)

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("AAPL", "AAPL"),
        (" msft ", "MSFT"),
        ("GOOGL", "GOOGL"),
        ("TSLA", "TSLA"),
        (" BRK.A", "BRK.A"),
        ("V", "V"),
    ],
)
def test_normalise_and_validate_ticker_valid(raw, expected):
    result = normalise_and_validate_ticker(raw)
    assert result == expected
    
@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        None,
    ],
)
def test_normalise_and_validate_ticker_empty_invalid(raw):
    with pytest.raises(InvalidTickerError) as exc_info:
        normalise_and_validate_ticker(raw)
    assert "cannot be" in str(exc_info.value)
    
@pytest.mark.parametrize(
    "raw",
    [
        "AAPL!",
        "AAP L",
        "AAAAAA",
        "A.B.C",
    ],
)
def test_normalise_and_validate_ticker_format_invalid(raw):
    with pytest.raises(InvalidTickerError):
        normalise_and_validate_ticker(raw)


