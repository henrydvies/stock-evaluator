from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

_STOCK_EVAL_ROOT = Path(__file__).resolve().parents[3]
for _env_path in (_STOCK_EVAL_ROOT / ".env", Path.cwd() / ".env"):
    if _env_path.is_file():
        load_dotenv(_env_path)

class Settings(BaseModel):
    """Settings configuration for the application.
    Args:
        BaseModel : Pydantic BaseModel for data validation.
    """
    app_name: str = "Stock Evaluator"
    environment: str = "development"
    debug: bool = True
    
settings = Settings()
