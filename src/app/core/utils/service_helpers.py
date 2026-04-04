from typing import Any, Dict, Optional
from math import isfinite


def _latest_numeric(data: Dict[Any, Any]) -> Optional[float]:
    """
    Get the most recent numeric value from a data dictionary.

    Args:
        data (Dict[Any, Any]):  The data dictionary.

    Returns:
        Optional[float]: The most recent numeric value or None if not found.
    """
    if not isinstance(data, dict) or not data:
        return None
    try:
        latest_period = sorted(data.keys())[-1]
        return _safe_float(data[latest_period])
    except Exception:
        return None
    
def _safe_float(value: Any) -> Optional[float]:
    """
    Safely convert a value to float.

    Args:
        value (Any): The value to convert.

    Returns:
        Optional[float]: The float value or None if conversion fails.
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        return None

    return num if isfinite(num) else None
    