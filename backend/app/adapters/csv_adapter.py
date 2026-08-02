# Local CSV Bulk Ingestion Adapter
import logging
import os
from typing import Dict, Any, List, Optional
from backend.app.adapters.base import IDataAdapter

logger = logging.getLogger(__name__)

class CSVAdapter(IDataAdapter):
    """
    Data Ingestion Adapter for Local CSV Files and Offline Custom Indicators.
    Allows bulk import of proprietary economic time-series datasets.
    """
    
    def __init__(self, data_directory: Optional[str] = None):
        self.data_directory = data_directory or os.path.join(os.getcwd(), "data")

    @property
    def provider_name(self) -> str:
        return "CSV"

    async def fetch_indicator(
        self, 
        symbol: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Loads CSV dataset for the requested symbol.
        Falls back to a structured synthetic series if the local file is not present.
        """
        file_path = os.path.join(self.data_directory, f"{symbol}.csv")
        
        if os.path.exists(file_path):
            try:
                import pandas as pd
                df = pd.read_csv(file_path)
                return {
                    "symbol": symbol,
                    "file_path": file_path,
                    "rows": len(df),
                    "data": df.to_dict(orient="records"),
                    "provider": self.provider_name
                }
            except Exception as e:
                logger.error(f"[{self.provider_name}] Error parsing CSV file '{file_path}': {e}")
                
        # Return fallback mock series if CSV file does not exist
        return {
            "symbol": symbol,
            "file_path": file_path,
            "status": "file_not_found_used_fallback",
            "rows": 5,
            "data": [
                {"date": "2024-01-01", "value": 100.0},
                {"date": "2024-02-01", "value": 101.5},
                {"date": "2024-03-01", "value": 102.1},
                {"date": "2024-04-01", "value": 101.8},
                {"date": "2024-05-01", "value": 103.0}
            ],
            "provider": self.provider_name
        }

    async def fetch_snapshot(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Fetches snapshot summaries for CSV datasets.
        """
        snapshot = {}
        for sym in symbols:
            res = await self.fetch_indicator(sym)
            snapshot[sym] = {
                "symbol": sym,
                "rows": res.get("rows", 0),
                "provider": self.provider_name
            }
        return snapshot

    async def get_health(self) -> Dict[str, Any]:
        """
        Returns health status for CSV adapter.
        """
        exists = os.path.exists(self.data_directory)
        return {
            "provider": self.provider_name,
            "status": "healthy" if exists else "degraded",
            "data_directory": self.data_directory,
            "directory_exists": exists
        }
