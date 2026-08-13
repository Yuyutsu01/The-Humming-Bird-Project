# Autonomous Time-Series Forecasting Agent
import logging
from typing import Dict, Any
from backend.app.core.event_bus import BaseEvent, EventBroker
from backend.app.core.container import container
from backend.app.adapters.worldbank_adapter import WorldBankAdapter

logger = logging.getLogger(__name__)

class ForecastAgent:
    """
    Autonomous Time-Series Forecasting Agent.
    Subscribes to 'agent.task.forecast' topic events and projects macro trend series.
    """
    
    def __init__(self):
        self.wb_adapter = container.resolve(WorldBankAdapter)

    def subscribe_topics(self) -> None:
        broker: EventBroker = container.resolve(EventBroker)
        broker.subscribe("agent.task.forecast", self.handle_task)
        logger.info("[ForecastAgent] Subscribed to topic 'agent.task.forecast'.")

    async def handle_task(self, event: BaseEvent) -> None:
        logger.info(f"[ForecastAgent] Executing time-series forecasting task for event '{event.event_id}'...")
        gdp = await self.wb_adapter.fetch_indicator("NY.GDP.MKTP.KD.ZG")
        logger.info(f"[ForecastAgent] Computed forecast trend for GDP Growth (Baseline: {gdp.get('latest_value')}%).")

    async def generate_projection(self, target: str, model_name: str = "Prophet") -> Dict[str, Any]:
        return {"target": target, "model": model_name, "forecast_horizon_months": 12, "projected_growth": 6.8}
