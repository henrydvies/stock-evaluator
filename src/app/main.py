from fastapi import FastAPI


from app.api.routes import tickers, price, fundamentals, eval
from app.core.config import settings

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
    
    # Evaluate all
    app.include_router(eval.router)
    
    return app

app = create_app()