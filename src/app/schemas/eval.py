from pydantic import BaseModel
from typing import Dict, Any, Optional

class EvalResponse(BaseModel):
    """Evaluation response schema.

    Args:
        BaseModel : Pydantic BaseModel for data validation.
    """
    ticker: str
    metrics: Dict[str, Dict[str, Optional[float]]]
