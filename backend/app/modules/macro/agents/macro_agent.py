# Autonomous Macroeconomic Analysis Agent
import logging
from typing import Dict, Any
from backend.app.core.event_bus import BaseEvent, EventBroker
from backend.app.core.container import container
from backend.app.adapters.fred_adapter import FREDAdapter
from backend.app.adapters.rbi_adapter import RBIAdapter

logger = logging.getLogger(__name__)

class MacroAgent:
    """
    Autonomous Macroeconomic Analysis Agent.
    Subscribes to 'agent.task.macro' topic events and computes shock transmission regressions.
    """
    
    def __init__(self):
        self.fred_adapter = container.resolve(FREDAdapter)
        self.rbi_adapter = container.resolve(RBIAdapter)

    def subscribe_topics(self) -> None:
        broker: EventBroker = container.resolve(EventBroker)
        broker.subscribe("agent.task.macro", self.handle_task)
        logger.info("[MacroAgent] Subscribed to topic 'agent.task.macro'.")

    async def handle_task(self, event: BaseEvent) -> None:
        logger.info(f"[MacroAgent] Executing macro transmission task for event '{event.event_id}'...")
        fed_data = await self.fred_adapter.fetch_indicator("FEDFUNDS")
        rbi_data = await self.rbi_adapter.fetch_indicator("RBI_REPO")
        logger.info(f"[MacroAgent] Evaluated Fed Rate ({fed_data.get('latest_value')}%) vs RBI Repo ({rbi_data.get('latest_value')}%).")

    async def compute_sensitivity(self, oil_price: float, fed_rate: float) -> Dict[str, Any]:
        cpi_change = (oil_price - 82.50) * 0.08 + (fed_rate - 5.25) * 0.12
        return {"oil_price": oil_price, "fed_rate": fed_rate, "simulated_cpi_delta": round(cpi_change, 2)}
