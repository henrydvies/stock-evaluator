from pydantic import BaseModel
from typing import Dict, Any, Optional

class EvalResponse(BaseModel):
    ticker: str
    metrics: Dict[str, Dict[str, Optional[float]]]
