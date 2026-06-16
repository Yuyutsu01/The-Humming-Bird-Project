from fastapi import APIRouter, HTTPException
from backend.app.services.news_engine import news_intelligence_engine

router = APIRouter(prefix="/news", tags=["News Intelligence"])

@router.get("")
def get_processed_news():
    """
    Returns aggregated financial news that has been deduplicated, sentiment-analyzed, and ranked.
    """
    try:
        return news_intelligence_engine.process_news()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process news: {str(e)}")
