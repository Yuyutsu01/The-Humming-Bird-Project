# Time-Series Metrics Repository Engine (TimescaleDB / InfluxDB interface)
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.app.repositories.base import IRepository

logger = logging.getLogger(__name__)

class TimeSeriesRepository(IRepository[Dict[str, Any]]):
    """
    Repository implementation for Time-Series Storage (TimescaleDB / InfluxDB).
    Manages high-frequency market ticks, historical indicator series, and bar data.
    """
    
    def __init__(self):
        # Keyed by symbol -> list of data points
        self._series_store: Dict[str, List[Dict[str, Any]]] = {}

    async def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the latest tick / data point for a given symbol identifier.
        """
        points = self._series_store.get(entity_id, [])
        return points[-1] if points else None

    async def list_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Lists all time-series points or points matching symbol filter.
        """
        symbol = filters.get("symbol") if filters else None
        if symbol and symbol in self._series_store:
            return self._series_store[symbol]
            
        all_points = []
        for p_list in self._series_store.values():
            all_points.extend(p_list)
        return all_points

    async def save(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appends a time-series data point.
        """
        symbol = entity.get("symbol") or "DEFAULT_SERIES"
        if symbol not in self._series_store:
            self._series_store[symbol] = []
            
        if "timestamp" not in entity:
            entity["timestamp"] = datetime.utcnow().isoformat()
            
        self._series_store[symbol].append(entity)
        return entity

    async def delete(self, entity_id: str) -> bool:
        """
        Clears time-series history for a symbol.
        """
        if entity_id in self._series_store:
            del self._series_store[entity_id]
            return True
        return False
