# Knowledge Graph & AI Copilot Plugin API Router
import logging
from fastapi import APIRouter, HTTPException, Query
from backend.app.services.ai_analyst import ai_analyst_service
from backend.app.services.relationship_engine import relationship_engine_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["Knowledge Graph & AI Plugin"])

@router.get("/ask")
async def ask_copilot(query: str = Query(..., description="Economic query in natural language")):
    """
    Answers an economic query by routing it through an LLM or local fallback engine.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        return await ai_analyst_service.ask_question(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analyst error: {str(e)}")

@router.get("/relationship/graph")
def get_macro_relationship_graph():
    """
    Returns nodes and edges for the macro-relationship knowledge graph.
    """
    try:
        return relationship_engine_service.get_graph()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationship/causality")
def trace_causality_path(
    source: str = Query(..., description="Source node ID (e.g. 'oil')"),
    target: str = Query(..., description="Target node ID (e.g. 'stock_market')")
):
    """
    Traces and explains the shortest causal pathway between a source variable and target variable.
    """
    try:
        path = relationship_engine_service.trace_causality(source, target)
        if not path:
            return {"message": "No direct relationship path found in the knowledge base."}
        return path
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
