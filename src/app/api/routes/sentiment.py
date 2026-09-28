from fastapi import APIRouter, Depends, HTTPException, status

from app.core.sentiment_service import SentimentService, get_sentiment_service
from app.providers.finnhub_client import FinnhubClientError
from app.schemas.sentiment import SentimentResponse
from app.schemas.ticker import ErrorResponse
from app.utils.ticker import InvalidTickerError

router = APIRouter(prefix="/sentiment", tags=["Sentiment"])


@router.get(
    "/{symbol}",
    response_model=SentimentResponse,
    responses={
        422: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
    },
)
async def get_sentiment(
    symbol: str,
    service: SentimentService = Depends(get_sentiment_service),
):
    """
    Narrative sentiment from Finnhub company news, scored with VADER.
    """
    try:
        return await service.get_sentiment_for_symbol(symbol)
    except InvalidTickerError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "INVALID_TICKER_FORMAT",
                "message": str(e),
                "details": f"Got '{symbol}'.",
            },
        )
    except FinnhubClientError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "FINNHUB_CLIENT_ERROR",
                "message": str(e),
                "details": "Error occurred while communicating with Finnhub.",
            },
        )
