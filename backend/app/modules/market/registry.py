# Market Module Registry Plugin Entrypoint
import logging
from fastapi import APIRouter
from backend.app.modules.base import BaseModule
from backend.app.modules.market.api import router
from backend.app.core.container import container
from backend.app.repositories.timeseries_repo import TimeSeriesRepository

logger = logging.getLogger(__name__)

class MarketModule(BaseModule):
    """
    Market Data Plugin Module.
    Manages live tickers, historical bars, and WebSockets streaming channels.
    """
    
    def initialize(self) -> None:
        logger.info("Initializing MarketModule...")
        self.ts_repo = container.resolve(TimeSeriesRepository)

    def register_routes(self) -> APIRouter:
        return router
