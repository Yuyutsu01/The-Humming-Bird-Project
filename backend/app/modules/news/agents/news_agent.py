# Autonomous News Intelligence Agent
import logging
from typing import Dict, Any
from backend.app.core.event_bus import BaseEvent, EventBroker
from backend.app.core.container import container
from backend.app.adapters.rss_adapter import RSSAdapter

logger = logging.getLogger(__name__)

class NewsAgent:
    """
    Autonomous News Intelligence Agent.
    Subscribes to 'agent.task.news' topic events, fetches RSS feeds,
    deduplicates headlines, and computes sentiment scores.
    """
    
    def __init__(self):
        self.rss_adapter = container.resolve(RSSAdapter)

    def subscribe_topics(self) -> None:
        broker: EventBroker = container.resolve(EventBroker)
        broker.subscribe("agent.task.news", self.handle_task)
        logger.info("[NewsAgent] Subscribed to topic 'agent.task.news'.")

    async def handle_task(self, event: BaseEvent) -> None:
        logger.info(f"[NewsAgent] Executing news intelligence task for event '{event.event_id}'...")
        feed = await self.rss_adapter.fetch_news_feed(limit=5)
        logger.info(f"[NewsAgent] Processed {len(feed)} news headlines successfully.")

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        score = 0.0
        if any(w in text_lower for w in ["rise", "surge", "gain", "boost", "growth"]):
            score += 0.5
        if any(w in text_lower for w in ["fall", "drop", "cut", "risk", "inflation"]):
            score -= 0.5
        return {"text": text, "sentiment_score": score, "sentiment": "bullish" if score > 0 else "bearish" if score < 0 else "neutral"}
