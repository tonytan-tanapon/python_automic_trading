from fastapi import APIRouter
from app.services.position_service import get_positions

router = APIRouter(prefix="/positions", tags=["Positions"])

@router.get("/")
def positions():
    return get_positions()