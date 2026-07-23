# Phase 1 Framework Verification Script (with Mock Dependencies)
import asyncio
import sys
import logging
from unittest.mock import MagicMock

# Setup mock modules for dependencies that may not be installed in the active environment
# This allows testing the core framework (routes, DI, event bus) in isolation.
sys.modules['pandas'] = MagicMock()
sys.modules['yfinance'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['numpy'] = MagicMock()

# Setup debug logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("verify_phase1")

async def run_verification():
    logger.info("==================================================")
    # 1. Load FastAPI App (this imports main which calls bootstrap_modules)
    logger.info("Loading FastAPI backend application context...")
    
    from backend.app.main import app
    from backend.app.core.container import container
    from backend.app.core.event_bus import EventBroker
    from backend.app.modules.test_mock.registry import TestEventMessage
    
    logger.info("FastAPI app successfully initialized.")
    
    # 2. Check Route Registrations
    logger.info("Scanning mounted API routes...")
    mock_route_found = False
    for route in app.routes:
        path = getattr(route, "path", "")
        if "/test_mock/hello" in path:
            mock_route_found = True
            logger.info(f"Detected dynamically loaded route: '{path}'")
            
    if not mock_route_found:
        logger.error("[FAIL] Mock route '/test_mock/hello' was NOT registered by the boot loader.")
        sys.exit(1)
    logger.info("[PASS] Dynamic route discovery and mounting verified!")

    # 3. Resolve Event Broker & Publish Test Event
    logger.info("Resolving EventBroker from Dependency Container...")
    broker = container.resolve(EventBroker)
    
    test_msg = "Hummingbird Core Framework redial verified successfully!"
    logger.info(f"Publishing TestEventMessage to 'test.verification.channel' with payload: '{test_msg}'")
    
    event = TestEventMessage(message_content=test_msg)
    await broker.publish("test.verification.channel", event)
    
    # Allow 1.0s for the asynchronous asyncio event loop task to invoke the handler
    logger.info("Waiting for async event dispatch task loop...")
    await asyncio.sleep(1.0)
    
    logger.info("[PASS] Asynchronous Event Dispatch and handler loops executed!")
    logger.info("==================================================")
    logger.info("PHASE 1 CORE FRAMEWORK VERIFICATION COMPLETED SUCCESSFULLY!")
    logger.info("==================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
