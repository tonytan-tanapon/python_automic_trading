from fastapi import APIRouter

from app.services.auto_trading_service import auto_trading_engine
from app.strategies import list_strategies

router = APIRouter(prefix="/auto-trading", tags=["Auto Trading"])


@router.get("/status")
def get_status():
    return auto_trading_engine.status()


@router.post("/start")
async def start_auto_trading():
    return await auto_trading_engine.start()


@router.post("/stop")
async def stop_auto_trading():
    return await auto_trading_engine.stop()


@router.post("/run-once")
async def run_once():
    return await auto_trading_engine.run_once()


@router.get("/strategies")
def get_strategies():
    return {
        "selected_strategy": auto_trading_engine.strategy_name,
        "available_strategies": list_strategies(),
    }
