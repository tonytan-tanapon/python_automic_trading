from fastapi import APIRouter, WebSocket
import asyncio

from app.services.market_data_service import get_price

router = APIRouter()


@router.websocket("/ws/price/{symbol}")
async def stream_price(websocket: WebSocket, symbol: str):
    await websocket.accept()

    try:
        while True:
            data = await asyncio.to_thread(get_price, symbol)
            await websocket.send_json(data)
            await asyncio.sleep(1)

    except Exception:
        await websocket.close()
