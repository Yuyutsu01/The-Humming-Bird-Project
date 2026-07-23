import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.routers import market, economy, ai, news, scenario, ws
from backend.app.services.market_data import market_data_service
from backend.app.core.boot import bootstrap_modules

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Life-cycle context manager. Initializes data caches on startup.
    """
    logger.info("Initializing Indian Economic Intelligence Platform Backend...")
    # Pre-seed cache with initial snapshot from yfinance
    try:
        await market_data_service.get_market_snapshot()
        logger.info("Market data cache pre-seeded successfully.")
    except Exception as e:
        logger.error(f"Failed to pre-seed market cache: {e}")
    yield
    logger.info("Shutting down backend services.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Platform detailing the domestic consequences of global economic and geopolitical developments.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS Middleware
# Allows cross-origin requests from our Next.js developer client (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints routers
app.include_router(market.router, prefix=settings.API_V1_STR)
app.include_router(economy.router, prefix=settings.API_V1_STR)
app.include_router(ai.router, prefix=settings.API_V1_STR)
app.include_router(news.router, prefix=settings.API_V1_STR)
app.include_router(scenario.router, prefix=settings.API_V1_STR)
app.include_router(ws.router, prefix=settings.API_V1_STR)

# Load dynamically registered agent modules
bootstrap_modules(app)

@app.get("/")
def get_root():
    return {
        "status": "active",
        "service": settings.PROJECT_NAME,
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    # Start server locally
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
