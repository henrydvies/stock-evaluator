from fastapi import APIRouter, Depends, HTTPException, status

from app.core.ticker_validation import TickerValidationService, TickerNotFoundError
from app.providers.yahoo_client import YFinanceYahooClient, YahooClientError
from app.utils.ticker import InvalidTickerError
from app.schemas.ticker import TickerValidationResponse, ErrorResponse

router = APIRouter(prefix="/tickers", tags=["Tickers"])

def get_ticker_validation_service() -> TickerValidationService:
    """
    Provides an instance of TickerValidationService with a YahooClient.
    Returns:
        TickerValidationService: An instance of TickerValidationService.
    """
    client = YFinanceYahooClient()
    return TickerValidationService(yahoo_client=client)

@router.get(
    "/{symbol}/validate", 
    response_model=TickerValidationResponse, 
    responses={
        422: {"model": ErrorResponse},
        404: {"model": ErrorResponse}, 
        502: {"model": ErrorResponse},
    },
)
async def validate_ticker(
    symbol: str,
    service: TickerValidationService = Depends(get_ticker_validation_service),
):
    """_summary_

    Args:
        symbol (str): _description_
        service (TickerValidationService, optional): _description_. Defaults to Depends(get_ticker_validation_service).
    """
    try:
        normalised = await service.validate_ticker(symbol)
        return TickerValidationResponse(symbol=normalised, valid=True)
    except InvalidTickerError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "INVALID_TICKER_FORMAT",
                "message": str(e),
                "details": f"Got '{symbol}'."
            },
        )
    
    except TickerNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "TICKER_NOT_FOUND",
                "message": str(e),
                "details": f"Symbol '{symbol}' does not exist."
            },
        )
    
    except YahooClientError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "YAHOO_CLIENT_ERROR",
                "message": str(e),
                "details": "Error occurred while communicating with Yahoo Finance."
            },
        )




