from fastapi import APIRouter, Query

from app.schemas.eval import EvalResponse
from app.metrics import evaluate_all

router = APIRouter()

@router.get("/eval", response_model=EvalResponse)
async def eval_stock(
    ticker: str = Query(
        ..., # This argument is required
        description="Stock ticker symbol to evaluate.",
    )
):
    """Evaluate stock metrics for a given ticker symbol.

    Args:
        ticker (str): Stock ticker symbol.
    Returns:
        EvalResponse: Evaluation results including metrics.
    """
    # Compute all metrics for the given ticker
    metrics = await evaluate_all(ticker)
    
    return EvalResponse(ticker=ticker.upper(), metrics=metrics)