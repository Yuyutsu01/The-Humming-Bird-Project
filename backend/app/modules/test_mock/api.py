# Mock Module API endpoints
from fastapi import APIRouter

router = APIRouter(prefix="/test_mock", tags=["Test Mock Module"])

@router.get("/hello")
def say_hello():
    """Simple verification route."""
    return {"message": "Hello from dynamically loaded mock module!"}
