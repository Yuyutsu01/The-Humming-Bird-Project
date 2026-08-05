# Market Module API Router and WebSocket Manager
import asyncio
import json
import logging
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from backend.app.services.market_data import market_data_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Market Plugin"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Active: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"Error broadcasting WS tick to client: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

@router.get("/market/snapshot")
async def get_market_snapshot():
    """
    Returns a complete snapshot of all global/Indian markets, commodities, forex, and bonds.
    """
    try:
        return await market_data_service.get_market_snapshot()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market snapshot: {str(e)}")

@router.get("/market/history")
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

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket channel streaming real-time Brownian ticks every 1.5s.
    """
    await manager.connect(websocket)
    try:
        snapshot = await market_data_service.get_market_snapshot()
        await websocket.send_text(json.dumps({
            "type": "snapshot",
            "data": snapshot
        }))
    except Exception as e:
        logger.error(f"Error sending initial WS snapshot: {e}")
        
    try:
        while True:
            await asyncio.sleep(1.5)
            ticks = market_data_service.generate_simulated_ticks()
            if ticks:
                await websocket.send_text(json.dumps({
                    "type": "tick",
                    "data": ticks
                }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket execution error: {e}")
        manager.disconnect(websocket)
