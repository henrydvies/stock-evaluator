from fastapi import FastAPI

from app.api.routes_eval import router as eval_router
from app.core.config import settings

def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    
    app = FastAPI(
        title=settings.app_name,)
    
    app.include_router(eval_router, prefix="/api")
    
    return app

app = create_app()