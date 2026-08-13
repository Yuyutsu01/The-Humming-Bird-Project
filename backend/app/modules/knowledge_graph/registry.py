# Knowledge Graph & AI Copilot Plugin Registry Entrypoint
import logging
from fastapi import APIRouter
from backend.app.modules.base import BaseModule
from backend.app.modules.knowledge_graph.api import router
from backend.app.modules.knowledge_graph.agents.graph_agent import GraphAgent
from backend.app.core.container import container
from backend.app.repositories.graph_repo import GraphRepository

logger = logging.getLogger(__name__)

class KnowledgeGraphModule(BaseModule):
    """
    Knowledge Graph & AI Analyst Plugin Module.
    Maps causal network transmission pathways and handles AI Copilot querying.
    """
    
    def initialize(self) -> None:
        logger.info("Initializing KnowledgeGraphModule...")
        self.graph_repo = container.resolve(GraphRepository)
        self.graph_agent = GraphAgent()
        self.graph_agent.subscribe_topics()

    def register_routes(self) -> APIRouter:
        return router
