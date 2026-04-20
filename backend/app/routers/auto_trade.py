from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.auto_trade_service import auto_trade_service

router = APIRouter(prefix="/auto-trade", tags=["Auto Trade"])


class RunOncePayload(BaseModel):
    symbol: str


@router.get("/status")
def get_auto_trade_status():
    return auto_trade_service.status()


@router.post("/run-once")
def run_once(payload: RunOncePayload):
    try:
        return auto_trade_service.run_once(payload.symbol)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
