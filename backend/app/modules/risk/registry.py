# Risk & Portfolio Analytics Plugin Registry Entrypoint
import logging
from fastapi import APIRouter
from backend.app.modules.base import BaseModule
from backend.app.modules.risk.api import router
from backend.app.modules.risk.agents.risk_agent import RiskAgent

logger = logging.getLogger(__name__)

class RiskModule(BaseModule):
    """
    Risk & Portfolio Analytics Plugin Module.
    Subscribes RiskAgent background listeners and evaluates sector vulnerabilities.
    """
    
    def initialize(self) -> None:
        logger.info("Initializing RiskModule...")
        self.risk_agent = RiskAgent()
        self.risk_agent.subscribe_topics()

    def register_routes(self) -> APIRouter:
        return router
