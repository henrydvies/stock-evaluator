from fastapi import APIRouter, Depends, HTTPException, status

from app.core.price_service import PriceService, PriceDataError
from app.providers.yahoo_client import YFinanceYahooClient, YahooClientError, YahooSymbolNotFoundError
from app.utils.ticker import InvalidTickerError
from app.schemas.price import PriceResponse
from app.schemas.ticker import ErrorResponse # Existing error schema

router = APIRouter(prefix="/price", tags=["Price"])

def get_price_service() -> PriceService:
    """
    Provides an instance of PriceService with a YahooClient.

    Returns:
        PriceService: An instance of PriceService.
    """
    client = YFinanceYahooClient()
    return PriceService(yahoo_client=client)

@router.get(
    "/{symbol}",
    response_model=PriceResponse,
    responses={
        422: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
    },
)
async def get_price(
    symbol: str,
    service: PriceService = Depends(get_price_service),
):
    """
    Get price data for a given stock symbol.

    Args:
        symbol (str): Stock ticker symbol.
        service (PriceService, optional): PriceService instance. Defaults to Depends(get_price_service).
    """
    try:
        return await service.get_price_for_symbol(symbol)
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
    except (YahooClientError, PriceDataError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "YAHOO_CLIENT_ERROR",
                "message": str(e),
                "details": "Error occurred while communicating with Yahoo Finance."
            },
        )