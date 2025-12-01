from pydantic import BaseModel


class Settings(BaseModel):
    """Settings configuration for the application.
    Args:
        BaseModel : Pydantic BaseModel for data validation.
    """
    app_name: str = "Stock Evaluator"
    environment: str = "development"
    debug: bool = True
    
settings = Settings()
