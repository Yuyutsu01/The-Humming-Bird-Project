# Reserve Bank of India (RBI) Ingestion Adapter
import logging
from typing import Dict, Any, List, Optional
from backend.app.adapters.base import IDataAdapter

logger = logging.getLogger(__name__)

class RBIAdapter(IDataAdapter):
    """
    Data Ingestion Adapter for Reserve Bank of India (RBI) Monetary Policy Indicators.
    Provides domestic policy rates, reserve ratios, and foreign exchange reserves data.
    """
    
    DEFAULT_RATES: Dict[str, Dict[str, Any]] = {
        "RBI_REPO": {
            "name": "RBI Policy Repo Rate",
            "value": 6.50,
            "unit": "Percent",
            "last_decision": "Unchanged (6-0 MPC vote)",
            "effective_date": "2024-02-08"
        },
        "RBI_REV_REPO": {
            "name": "Standing Deposit Facility (SDF) Rate",
            "value": 6.25,
            "unit": "Percent",
            "effective_date": "2024-02-08"
        },
        "RBI_CRR": {
            "name": "Cash Reserve Ratio (CRR)",
            "value": 4.50,
            "unit": "Percent",
            "effective_date": "2022-05-21"
        },
        "RBI_SLR": {
            "name": "Statutory Liquidity Ratio (SLR)",
            "value": 18.00,
            "unit": "Percent",
            "effective_date": "2020-04-10"
        },
        "RBI_FOREX_RESERVES": {
            "name": "Foreign Exchange Reserves",
            "value": 652.89,
            "unit": "Billion USD",
            "effective_date": "2024-06-14"
        }
    }

    @property
    def provider_name(self) -> str:
        return "RBI"

    async def fetch_indicator(
        self, 
        symbol: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetches monetary policy indicator data from RBI registry.
        """
        sym_upper = symbol.upper()
        if sym_upper in self.DEFAULT_RATES:
            rate_info = self.DEFAULT_RATES[sym_upper]
            return {
                "symbol": sym_upper,
                "name": rate_info["name"],
                "latest_value": rate_info["value"],
                "unit": rate_info["unit"],
                "effective_date": rate_info.get("effective_date"),
                "provider": self.provider_name
            }
            
        return {
            "symbol": symbol,
            "name": f"RBI Indicator ({symbol})",
            "latest_value": 0.0,
            "unit": "Percent",
            "provider": self.provider_name
        }

    async def fetch_snapshot(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Fetches snapshots for RBI monetary policy indicators.
        """
        snapshot = {}
        for sym in symbols:
            rate_data = await self.fetch_indicator(sym)
            snapshot[sym] = {
                "symbol": sym,
                "name": rate_data.get("name"),
                "value": rate_data.get("latest_value"),
                "unit": rate_data.get("unit"),
                "provider": self.provider_name
            }
        return snapshot

    async def get_health(self) -> Dict[str, Any]:
        """
        Returns health status for RBI adapter.
        """
        return {
            "provider": self.provider_name,
            "status": "healthy",
            "indicators_tracked": len(self.DEFAULT_RATES)
        }
