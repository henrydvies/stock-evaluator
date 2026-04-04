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
    