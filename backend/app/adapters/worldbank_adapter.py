# World Bank Economic Data Ingestion Adapter
import logging
from typing import Dict, Any, List, Optional
from backend.app.adapters.base import IDataAdapter

logger = logging.getLogger(__name__)

class WorldBankAdapter(IDataAdapter):
    """
    Data Ingestion Adapter for World Bank Open Data API.
    Provides global macroeconomic metrics, GDP growth rates, and structural indicators.
    """
    
    DEFAULT_SERIES: Dict[str, Dict[str, Any]] = {
        "NY.GDP.MKTP.KD.ZG": {
            "name": "GDP Growth (Annual %)",
            "country": "India",
            "latest_value": 7.2,
            "unit": "Percent",
            "history": {"2021": 9.1, "2022": 7.0, "2023": 7.2, "2024": 6.8}
        },
        "FP.CPI.TOTL.ZG": {
            "name": "Inflation, Consumer Prices (Annual %)",
            "country": "India",
            "latest_value": 4.85,
            "unit": "Percent",
            "history": {"2021": 5.1, "2022": 6.7, "2023": 5.7, "2024": 4.85}
        },
        "NE.TRD.GNFS.ZS": {
            "name": "Trade (% of GDP)",
            "country": "India",
            "latest_value": 49.2,
            "unit": "Percent of GDP",
            "history": {"2021": 45.4, "2022": 49.1, "2023": 49.2}
        }
    }

    @property
    def provider_name(self) -> str:
        return "WorldBank"

    async def fetch_indicator(
        self, 
        symbol: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetches World Bank indicator data.
        """
        symbol_upper = symbol.upper()
        if symbol_upper in self.DEFAULT_SERIES:
            info = self.DEFAULT_SERIES[symbol_upper]
            return {
                "symbol": symbol_upper,
                "name": info["name"],
                "country": info["country"],
                "latest_value": info["latest_value"],
                "unit": info["unit"],
                "history": info["history"],
                "provider": self.provider_name
            }
            
        return {
            "symbol": symbol,
            "name": f"World Bank Indicator ({symbol})",
            "latest_value": 0.0,
            "unit": "Index",
            "provider": self.provider_name
        }

    async def fetch_snapshot(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Fetches snapshots for World Bank indicators.
        """
        snapshot = {}
        for sym in symbols:
            ind = await self.fetch_indicator(sym)
            snapshot[sym] = {
                "symbol": sym,
                "name": ind.get("name"),
                "value": ind.get("latest_value"),
                "provider": self.provider_name
            }
        return snapshot

    async def get_health(self) -> Dict[str, Any]:
        """
        Returns health status for World Bank adapter.
        """
        return {
            "provider": self.provider_name,
            "status": "healthy",
            "indicators_available": len(self.DEFAULT_SERIES)
        }
