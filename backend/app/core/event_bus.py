# Event Broker and Schema Definitions
import asyncio
import uuid
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Callable, Awaitable
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# --- Event Schema Definitions ---
# Events represent the message packets sent between decoupled agents.

class BaseEvent(BaseModel):
    """
    Base event structure carrying standard metadata.
    All custom module events must inherit from this model.
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message UUID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time when the event occurred")
    version: str = "1.0"


# --- Event Broker Interfaces ---

class EventBroker(ABC):
    """
    Abstract interface for publishing and subscribing to events.
    Enables agents to communicate without direct service dependency imports.
    """
    
    @abstractmethod
    async def publish(self, topic: str, event: BaseEvent) -> None:
        """
        Publishes an event message onto a topic channel.
        """
        pass
        
    @abstractmethod
    def subscribe(self, topic: str, handler: Callable[[BaseEvent], Awaitable[None]]) -> None:
        """
        Registers an async callback handler to listen for events on a topic channel.
        """
        pass


# --- In-Memory Asynchronous Event Broker Implementation ---

class InMemoryEventBus(EventBroker):
    """
    Asynchronous in-memory implementation of the Event Broker.
    Serves as the local event broker, routing messages within the async loop.
    """
    
    def __init__(self):
        # Maps topic channels to list of subscriber callbacks
        self._subscribers: Dict[str, List[Callable[[BaseEvent], Awaitable[None]]]] = {}
        
    async def publish(self, topic: str, event: BaseEvent) -> None:
        """
        Dispatches the event to all registered topic subscribers.
        Executes handlers concurrently in background tasks so the publisher does not block.
        """
        if topic not in self._subscribers:
            logger.debug(f"Event published to topic '{topic}' with 0 subscribers.")
            return
            
        logger.info(f"Publishing event {event.event_id} to topic '{topic}' with {len(self._subscribers[topic])} subscribers.")
        
        # Dispatch concurrently to avoid blocking the caller
        for handler in self._subscribers[topic]:
            asyncio.create_task(self._safe_execute_handler(handler, event, topic))
            
    def subscribe(self, topic: str, handler: Callable[[BaseEvent], Awaitable[None]]) -> None:
        """
        Subscribes a callback handler to a specific topic channel.
        """
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)
        logger.info(f"Handler {handler.__name__ if hasattr(handler, '__name__') else str(handler)} subscribed to topic '{topic}'.")

    async def _safe_execute_handler(self, handler: Callable[[BaseEvent], Awaitable[None]], event: BaseEvent, topic: str) -> None:
        """
        Executes a callback handler safely, logging any exceptions.
        """
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error handling event {event.event_id} on topic '{topic}' in handler {handler}: {e}", exc_info=True)
