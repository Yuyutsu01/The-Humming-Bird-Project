# Forecast & Economic Plugin Registry Entrypoint
import logging
from fastapi import APIRouter
from backend.app.modules.base import BaseModule
from backend.app.modules.forecast.api import router
from backend.app.core.container import container
from backend.app.adapters.worldbank_adapter import WorldBankAdapter

logger = logging.getLogger(__name__)

class ForecastModule(BaseModule):
    """
    Forecasting & Economic Data Plugin Module.
    Models trend extrapolations, confidence intervals, and alternative metrics.
    """
    
    def initialize(self) -> None:
        logger.info("Initializing ForecastModule...")
        self.worldbank_adapter = container.resolve(WorldBankAdapter)

    def register_routes(self) -> APIRouter:
        return router
