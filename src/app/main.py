from fastapi import FastAPI

# Load .env before routes/metrics import (metrics construct Finnhub client at import time).
from app.core.config import settings
from app.api.routes import tickers, price, fundamentals, technical, eval, sentiment
def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    
    app = FastAPI(
        title=settings.app_name,)
    
    app.include_router(tickers.router)
    
    # Individual metric routes
    app.include_router(price.router)
    app.include_router(fundamentals.router)
    app.include_router(technical.router)
    app.include_router(sentiment.router)

    # Evaluate all
    app.include_router(eval.router)
    
    return app

app = create_app()