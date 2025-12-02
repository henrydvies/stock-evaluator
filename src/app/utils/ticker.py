import re

TICKER_REGEX = re.compile(r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$')

class InvalidTickerError(ValueError):
    """
    Raised when a ticker symbol is invalid for its format.
    """
    pass

def normalise_and_validate_ticker(raw: str) -> str:
    """
    Normalise and validate a ticker symbol.
    Args:
        raw (str): The raw ticker symbol input.
    Returns:
        str: The normalised ticker symbol.
    """
    
    if raw is None:
        raise InvalidTickerError("Ticker symbol cannot be None.")
    
    symbol = raw.strip().upper()
    if not symbol:
        raise InvalidTickerError("Ticker symbol cannot be empty.")
    
    if not TICKER_REGEX.match(symbol):
        raise InvalidTickerError(f"Invalid ticker symbol format: '{raw}'")
    
    return symbol