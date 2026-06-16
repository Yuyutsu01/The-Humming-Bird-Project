from fastapi import APIRouter, HTTPException, Query
from backend.app.services.market_data import market_data_service

router = APIRouter(prefix="/market", tags=["Market Data"])

@router.get("/snapshot")
async def get_market_snapshot():
    """
    Returns a complete snapshot of all global/Indian markets, commodities, forex, and bonds.
    """
    try:
        return await market_data_service.get_market_snapshot()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market snapshot: {str(e)}")

@router.get("/history")
async def get_market_history(
    name: str = Query(..., description="Asset name (e.g. 'Nifty 50', 'Gold', 'Brent Crude')"),
    period: str = Query("1mo", description="Historical period ('1mo', '3mo', '1y')"),
    interval: str = Query("1d", description="Data interval ('1d', '1wk', '1mo')")
):
    """
    Returns historical candlestick/bar data for charting an asset.
    """
    try:
        return await market_data_service.get_historical_bars(name, period, interval)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history for {name}: {str(e)}")
