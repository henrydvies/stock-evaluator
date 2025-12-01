async def get_current_price(ticker: str) -> float:
    """Fetch the current stock price for a given ticker.

    Args:
        ticker (str): Stock ticker symbol.
    Returns:
        float: Current stock price.
    """
    # Placeholder implementation
    STOCK_PRICES = {
        "AAPL": 199.40, 
        "GOOGL": 2750.50,
        "MSFT": 299.00
    }  
    
    stock_price = STOCK_PRICES.get(ticker.upper(), 0)  # Default price if ticker not found
    
    return float(stock_price)