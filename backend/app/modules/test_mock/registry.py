# Mock Module Registry Entrypoint
import logging
from fastapi import APIRouter
from backend.app.modules.base import BaseModule
from backend.app.modules.test_mock.api import router
from backend.app.core.container import container
from backend.app.core.event_bus import EventBroker, BaseEvent

logger = logging.getLogger(__name__)

class TestEventMessage(BaseEvent):
    """Simple test event carries verification message text."""
    message_content: str

class TestMockModule(BaseModule):
    """
    Mock Module implementation.
    Validates dynamic registry discovery, DI interface resolving,
    and AsyncIO event bus loopback notifications.
    """
    
    def initialize(self) -> None:
        logger.info("Initializing TestMockModule...")
        
        # 1. Resolve Event Broker from DI Container
        event_broker = container.resolve(EventBroker)
        
        # 2. Subscribe to verification channel
        async def verify_handler(event: BaseEvent) -> None:
            # Cast event to specific type
            if isinstance(event, TestEventMessage):
                logger.info(f"[VERIFICATION SUCCESS] TestMockModule received verification event: '{event.message_content}'")
            else:
                logger.info(f"TestMockModule received generic event: {event.event_id}")
                
        # Register subscriber callback directly and synchronously
        event_broker.subscribe("test.verification.channel", verify_handler)
        logger.info("TestMockModule registered subscriber callback successfully.")
        
    def register_routes(self) -> APIRouter:
        return router
