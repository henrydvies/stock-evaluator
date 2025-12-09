from fastapi import APIRouter, Depends, HTTPException, status

from app.metrics.fundamentals import get_fundamentals_service
from app.core.fundamentals_service import FundamentalsService, FundamentalsDataError
from app.schemas.fundamentals import FundamentalsResponse
from app.schemas.ticker import ErrorResponse
from app.utils.ticker import InvalidTickerError
from app.providers.yahoo_client import YFinanceYahooClient, YahooClientError, YahooSymbolNotFoundError

router = APIRouter(prefix="/fundamentals", tags=["Fundamentals"])

@router.get(
    "/{symbol}",
    response_model=FundamentalsResponse,
    responses={
        422: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
    },
)
async def get_fundamentals(
    symbol: str,
    service: FundamentalsService = Depends(get_fundamentals_service),
):
    """
    Get fundamentals data for a given stock symbol.

    Args:
        symbol (str): Stock ticker symbol.
        service (FundamentalsService, optional): FundamentalsService instance. Defaults to Depends(get_fundamentals_service).
    """
    try:
        return await service.get_fundamentals_for_symbol(symbol)
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
    except (YahooClientError, FundamentalsDataError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "YAHOO_CLIENT_ERROR",
                "message": str(e),
                "details": "Error occurred while communicating with Yahoo Finance."
            },
        )
    except FundamentalsDataError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "FUNDAMENTALS_DATA_ERROR",
                "message": str(e),
                "details": "Error occurred while retrieving fundamentals data."
            },
        )
    
    
    