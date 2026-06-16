from fastapi import APIRouter, HTTPException, Query
from backend.app.services.economic_data import economic_data_service
from backend.app.services.forecasting import forecasting_service
from backend.app.services.alternative_data import alternative_data_service

router = APIRouter(prefix="/economy", tags=["Economic Data"])

@router.get("/indicators")
def get_all_indicators():
    """
    Returns all pre-seeded macroeconomic indicators.
    """
    try:
        return economic_data_service.get_all_indicators()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/{region}/{name}")
def get_indicator_history(region: str, name: str):
    """
    Returns historical data series for a specific economic indicator.
    """
    data = economic_data_service.get_indicator(region, name)
    if not data:
        raise HTTPException(status_code=404, detail="Macro indicator not found")
    return data

@router.get("/forecast")
def get_economic_forecast(
    model: str = Query(..., description="Forecasting model (e.g. 'Prophet', 'LSTM', 'XGBoost')"),
    target: str = Query(..., description="Target variable (e.g. 'CPI Inflation', 'Oil Prices')")
):
    """
    Runs a simulation forecast using the specified machine learning model and target variable.
    """
    res = forecasting_service.get_forecast(model, target)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@router.get("/alternative")
def get_alternative_data():
    """
    Returns alternative data points like port traffic and satellite activity indicators.
    """
    try:
        return alternative_data_service.get_alternative_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
