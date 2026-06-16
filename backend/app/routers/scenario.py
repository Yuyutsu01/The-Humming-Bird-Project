from fastapi import APIRouter, HTTPException, Query
from backend.app.services.scenario_simulator import scenario_simulator_service

router = APIRouter(prefix="/scenario", tags=["Scenario Simulator"])

@router.get("/simulate")
def run_economic_simulation(
    oil_price: float = Query(82.50, description="Crude Oil price in USD per barrel", ge=40.0, le=200.0),
    fed_rate: float = Query(5.25, description="US Fed interest rate in percent", ge=0.0, le=10.0),
    geopolitical_risk: float = Query(40.0, description="Geopolitical risk index (0 to 100)", ge=0.0, le=100.0)
):
    """
    Executes a sensitivity simulation mapping shifts in crude oil, Fed rates, and geopolitics to domestic metrics.
    """
    try:
        return scenario_simulator_service.simulate(oil_price, fed_rate, geopolitical_risk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation execution failed: {str(e)}")
