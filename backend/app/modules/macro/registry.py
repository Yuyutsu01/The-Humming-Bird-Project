# Macroeconomic Sensitivity Plugin Registry Entrypoint
import logging
from fastapi import APIRouter
from backend.app.modules.base import BaseModule
from backend.app.modules.macro.api import router
from backend.app.core.container import container
from backend.app.adapters.fred_adapter import FREDAdapter
from backend.app.adapters.rbi_adapter import RBIAdapter

logger = logging.getLogger(__name__)

class MacroModule(BaseModule):
    """
    Macroeconomic Transmission & Sensitivity Plugin Module.
    Models transmission channels and solves macro parameter sensitivity offsets.
    """
    
    def initialize(self) -> None:
        logger.info("Initializing MacroModule...")
        self.fred_adapter = container.resolve(FREDAdapter)
        self.rbi_adapter = container.resolve(RBIAdapter)

    def register_routes(self) -> APIRouter:
        return router
