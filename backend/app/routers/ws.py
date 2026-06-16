import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.services.market_data import market_data_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSockets Streaming"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                # Handle broken connections gracefully
                logger.warning(f"Error broadcasting to client: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Send initial snapshot immediately so client is populated
    try:
        snapshot = await market_data_service.get_market_snapshot()
        await websocket.send_text(json.dumps({
            "type": "snapshot",
            "data": snapshot
        }))
    except Exception as e:
        logger.error(f"Error sending initial snapshot to client: {e}")
        
    try:
        # Keep connection open and broadcast ticking feeds
        while True:
            # Stream every 1.5 seconds to feel live without overloading network
            await asyncio.sleep(1.5)

            # Generate simulated small Brownian shifts
            ticks = market_data_service.generate_simulated_ticks()
            
            # Formulate tick update
            if ticks:
                await websocket.send_text(json.dumps({
                    "type": "tick",
                    "data": ticks
                }))
                
                # Check for random alert conditions to satisfy "Alerting System" requirement
                # Alert when: Brent Crude exceeds $85, Gold exceeds $2360, or a random headline event
                import random
                if random.random() < 0.05:  # 5% chance of an economic alert tick
                    alerts = []
                    brent = ticks.get("Brent Crude", {})
                    if brent and brent.get("price", 0.0) > 83.50:
                        alerts.append({
                            "title": "Alert: Crude Oil Price Escalation",
                            "severity": "Medium",
                            "message": f"Brent crude rises above baseline to ${brent['price']}/bbl. Sector margins under alert."
                        })
                    
                    gold = ticks.get("Gold", {})
                    if gold and gold.get("price", 0.0) > 2360.0:
                        alerts.append({
                            "title": "Alert: Safe Haven Gold Surge",
                            "severity": "Low",
                            "message": f"Gold pushes past ${gold['price']}/oz, signaling defensive global asset hedging."
                        })
                        
                    if alerts:
                        await websocket.send_text(json.dumps({
                            "type": "alerts",
                            "data": alerts
                        }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket execution error: {e}")
        manager.disconnect(websocket)
