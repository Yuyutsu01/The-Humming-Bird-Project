# Data Adapter Abstract Base Protocol Interface
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class IDataAdapter(ABC):
    """
    Abstract interface for all EIOS Data Provider Adapters.
    Decouples market and macroeconomic data sources behind provider-agnostic port interfaces.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Returns the unique name of the data provider (e.g. 'yfinance', 'FRED', 'WorldBank').
        """
        pass
        
    @abstractmethod
    async def fetch_indicator(
        self, 
        symbol: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetches normalized historical time-series data for a given indicator symbol.
        """
        pass
        
    @abstractmethod
    async def fetch_snapshot(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Fetches real-time or latest available data snapshots for a list of symbols.
        """
        pass
        
    @abstractmethod
    async def get_health(self) -> Dict[str, Any]:
        """
        Checks connectivity and operational status for the data provider.
        """
        pass
