from fastapi import FastAPI

from app.api.routes import tickers, price
from app.core.config import settings

def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    
    app = FastAPI(
        title=settings.app_name,)
    
    app.include_router(tickers.router)
    app.include_router(price.router)
    
    return app

app = create_app()