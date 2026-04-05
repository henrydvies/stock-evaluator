from fastapi import APIRouter, HTTPException, Depends, status

from app.metrics.technical import get_technical_service
from app.core.technical_service import TechnicalService, TechnicalDataError
from app.schemas.technical import TechnicalResponse
from app.schemas.ticker import ErrorResponse
from app.utils.ticker import InvalidTickerError
from app.providers.yahoo_client import YFinanceYahooClient, YahooClientError, YahooSymbolNotFoundError

router = APIRouter(prefix="/technical", tags=["Technical"])

@router.get(
    "/{symbol}",        
    response_model=TechnicalResponse,
    responses={
        422: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
    },
)

async def get_technical(
    symbol: str,
    service: TechnicalService = Depends(get_technical_service),
):
    """
    Get technical data for a given stock symbol.

    Args:
        symbol (str): Stock ticker symbol.
        service (TechnicalService, optional): TechnicalService instance. Defaults to Depends(get_technical_service).
    """
    try:
        return await service.get_technical_for_symbol(symbol)
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
    except (YahooClientError, TechnicalDataError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "YAHOO_CLIENT_ERROR",
                "message": str(e),
                "details": "Error occurred while communicating with Yahoo Finance."
            },
        )
    except TechnicalDataError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "TECHNICAL_DATA_ERROR",
                "message": str(e),
                "details": "Error occurred while retrieving technical data."
            },
        )