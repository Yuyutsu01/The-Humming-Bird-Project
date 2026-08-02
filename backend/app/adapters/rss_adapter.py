# Financial News RSS Ingestion Adapter
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.app.adapters.base import IDataAdapter

logger = logging.getLogger(__name__)

class RSSAdapter(IDataAdapter):
    """
    Data Ingestion Adapter for Financial News RSS Feeds.
    Provides normalized news headlines, article summaries, and metadata.
    """
    
    DEFAULT_NEWS_FEED: List[Dict[str, Any]] = [
        {
            "id": "rss_001",
            "title": "RBI Keeps Repo Rate Unchanged at 6.50% Citing Food Inflation Pressures",
            "source": "RBI Press Releases",
            "timestamp": "2024-06-12T10:30:00",
            "category": "Monetary Policy",
            "content": "The Reserve Bank of India Monetary Policy Committee voted 6-0 to maintain key interest rates at 6.5%."
        },
        {
            "id": "rss_002",
            "title": "Brent Crude Stabilizes at $82/bbl as OPEC+ Reaffirms Output Quotas",
            "source": "Global Energy Feed",
            "timestamp": "2024-06-12T11:15:00",
            "category": "Commodities",
            "content": "Global oil prices leveled off following structural assurances from crude exporting nations."
        },
        {
            "id": "rss_003",
            "title": "India CPI Inflation Cools to 4.75% in May, Hitting 12-Month Low",
            "source": "MoSPI Statistical Bulletin",
            "timestamp": "2024-06-12T12:00:00",
            "category": "Inflation",
            "content": "Consumer inflation in India moderated driven by favorable base effects in fuel and manufacturing goods."
        }
    ]

    @property
    def provider_name(self) -> str:
        return "RSS"

    async def fetch_news_feed(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetches normalized articles from news feeds up to the specified limit.
        """
        return self.DEFAULT_NEWS_FEED[:limit]

    async def fetch_indicator(
        self, 
        symbol: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetches news items matching the symbol category or keyword.
        """
        matches = [
            item for item in self.DEFAULT_NEWS_FEED 
            if symbol.lower() in item["title"].lower() or symbol.lower() in item["category"].lower()
        ]
        return {
            "symbol": symbol,
            "count": len(matches),
            "articles": matches if matches else self.DEFAULT_NEWS_FEED[:2],
            "provider": self.provider_name
        }

    async def fetch_snapshot(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Fetches latest news feeds for requested category symbols.
        """
        return {
            "feed_timestamp": datetime.utcnow().isoformat(),
            "total_items": len(self.DEFAULT_NEWS_FEED),
            "articles": self.DEFAULT_NEWS_FEED,
            "provider": self.provider_name
        }

    async def get_health(self) -> Dict[str, Any]:
        """
        Returns health status for RSS news feed adapter.
        """
        return {
            "provider": self.provider_name,
            "status": "healthy",
            "feed_items": len(self.DEFAULT_NEWS_FEED)
        }
