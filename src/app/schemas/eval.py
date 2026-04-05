from pydantic import BaseModel
from typing import Dict, Optional

class EvalResponse(BaseModel):
    ticker: str
    metrics: Dict[str, Dict[str, Optional[float | bool]]]
