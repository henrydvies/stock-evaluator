from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.eval import EvalResponse
from app.metrics import evaluate_all
from app.schemas.ticker import ErrorResponse

from app.utils.ticker import InvalidTickerError
from app.providers.yahoo_client import YahooClientError, YahooSymbolNotFoundError
from app.core.price_service import PriceDataError
from app.core.fundamentals_service import FundamentalsDataError


router = APIRouter(prefix="/eval", tags=["Evaluation"])

@router.get(
    "/{symbol}", 
    response_model=EvalResponse,
    responses={
        422: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
        
})
async def evaluate_stock(
    symbol: str,
):

    """Evaluate stock metrics for a given ticker symbol.

    Args:
        ticker (str): Stock ticker symbol.
    Returns:
        EvalResponse: Evaluation results including metrics.
    """
    try:
        metrics = await evaluate_all(symbol)
        return EvalResponse(ticker=symbol, metrics=metrics)
    except InvalidTickerError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "INVALID_TICKER_FORMAT",
                "message": str(e),
                "details": f"Got '{symbol}'."
            },
        )
    except YahooSymbolNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "TICKER_NOT_FOUND",
                "message": str(e),
                "details": f"Symbol '{symbol}' does not exist."
            },
        )
    except (YahooClientError, PriceDataError, FundamentalsDataError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "YAHOO_CLIENT_ERROR",
                "message": str(e),
                "details": "Error occurred while communicating with Yahoo Finance."
            },
        )
    
    