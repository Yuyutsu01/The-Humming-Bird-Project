# Repository Abstract Base Protocol Interface
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    """
    Abstract interface for all EIOS Data Repositories.
    Decouples storage engines (PostgreSQL, TimescaleDB, Neo4j, Qdrant) from domain logic.
    """
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Retrieves a single domain entity by unique identifier.
        """
        pass
        
    @abstractmethod
    async def list_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        Retrieves a list of entities matching optional filter parameters.
        """
        pass
        
    @abstractmethod
    async def save(self, entity: T) -> T:
        """
        Persists or updates an entity in the underlying database storage.
        """
        pass
        
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """
        Removes an entity by identifier from storage.
        """
        pass
