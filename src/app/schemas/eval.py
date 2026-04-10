from typing import Any, Dict

from pydantic import BaseModel


class EvalResponse(BaseModel):
    ticker: str
    metrics: Dict[str, Dict[str, Any]]
