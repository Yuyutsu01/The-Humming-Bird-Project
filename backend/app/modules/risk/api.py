# Risk & Portfolio Analytics Plugin API Router
import logging
from fastapi import APIRouter, HTTPException
from backend.app.core.container import container
from backend.app.modules.risk.agents.risk_agent import RiskAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/risk", tags=["Risk & Portfolio Plugin"])

@router.get("/sectors")
async def get_sector_risk_scores():
    """
    Returns risk vulnerability scores across corporate sectors.
    """
    try:
        agent = RiskAgent()
        return await agent.evaluate_sector_risks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch risk metrics: {str(e)}")
