# Dependency Injection Container Configuration
import logging
from typing import Dict, Any, Callable
from backend.app.core.event_bus import InMemoryEventBus, EventBroker
from backend.app.adapters.yfinance_adapter import YFinanceAdapter
from backend.app.adapters.fred_adapter import FREDAdapter
from backend.app.adapters.worldbank_adapter import WorldBankAdapter
from backend.app.adapters.rbi_adapter import RBIAdapter
from backend.app.adapters.rss_adapter import RSSAdapter
from backend.app.adapters.csv_adapter import CSVAdapter

from backend.app.repositories.postgres_repo import PostgresRepository
from backend.app.repositories.timeseries_repo import TimeSeriesRepository
from backend.app.repositories.graph_repo import GraphRepository
from backend.app.repositories.vector_repo import VectorRepository

logger = logging.getLogger(__name__)

class DependencyContainer:
    """
    A pure Python Dependency Injection Container.
    Decouples routes and service instantiation from concrete constructors
    by keeping a registry of shared singleton service interfaces.
    """
    
    def __init__(self):
        # Stores instantiated singleton objects
        self._singletons: Dict[str, Any] = {}
        # Stores callable provider functions for transient bindings
        self._providers: Dict[str, Callable[..., Any]] = {}
        
    def register_singleton(self, service_type: type, instance: Any) -> None:
        """
        Binds a concrete instance as a singleton for the given service type interface.
        """
        key = service_type.__name__
        self._singletons[key] = instance
        logger.info(f"Registered singleton instance for interface '{key}'.")
        
    def register_provider(self, service_type: type, provider: Callable[..., Any]) -> None:
        """
        Binds a factory provider callable to generate transient instances of the service.
        """
        key = service_type.__name__
        self._providers[key] = provider
        logger.info(f"Registered provider factory for interface '{key}'.")
        
    def resolve(self, service_type: type) -> Any:
        """
        Resolves and returns the bound service instance for the requested type.
        Raises ValueError if the service interface has no active binding.
        """
        key = service_type.__name__
        
        # 1. Check singletons first
        if key in self._singletons:
            return self._singletons[key]
            
        # 2. Check transient providers
        if key in self._providers:
            return self._providers[key]()
            
        raise ValueError(f"Dependency injection failed: Interface '{key}' is not registered.")


# Instantiate the global DI Container instance
container = DependencyContainer()

# --- Core Framework Bootstrap bindings ---
# Register the shared InMemoryEventBus as the default EventBroker singleton
container.register_singleton(EventBroker, InMemoryEventBus())

# --- Data Ingestion Adapter Singletons ---
container.register_singleton(YFinanceAdapter, YFinanceAdapter())
container.register_singleton(FREDAdapter, FREDAdapter())
container.register_singleton(WorldBankAdapter, WorldBankAdapter())
container.register_singleton(RBIAdapter, RBIAdapter())
container.register_singleton(RSSAdapter, RSSAdapter())
container.register_singleton(CSVAdapter, CSVAdapter())

# --- Database Storage Repository Singletons ---
container.register_singleton(PostgresRepository, PostgresRepository())
container.register_singleton(TimeSeriesRepository, TimeSeriesRepository())
container.register_singleton(GraphRepository, GraphRepository())
container.register_singleton(VectorRepository, VectorRepository())
