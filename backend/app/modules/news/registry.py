# News Intelligence Module Registry Plugin Entrypoint
import logging
from fastapi import APIRouter
from backend.app.modules.base import BaseModule
from backend.app.modules.news.api import router
from backend.app.modules.news.agents.news_agent import NewsAgent
from backend.app.core.container import container
from backend.app.adapters.rss_adapter import RSSAdapter
from backend.app.repositories.vector_repo import VectorRepository

logger = logging.getLogger(__name__)

class NewsModule(BaseModule):
    """
    News Intelligence Plugin Module.
    Deduplicates financial news streams, computes sentiment scores, and manages vector embeddings.
    """
    
    def initialize(self) -> None:
        logger.info("Initializing NewsModule...")
        self.rss_adapter = container.resolve(RSSAdapter)
        self.vector_repo = container.resolve(VectorRepository)
        self.news_agent = NewsAgent()
        self.news_agent.subscribe_topics()

    def register_routes(self) -> APIRouter:
        return router
