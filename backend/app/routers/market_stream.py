from fastapi import APIRouter, WebSocket
from ib_insync import Stock
from app.services.ib_client import connect_ib

router = APIRouter()

@router.websocket("/ws/price/{symbol}")
async def stream_price(websocket: WebSocket, symbol: str):

    await websocket.accept()

    ib = connect_ib()

    contract = Stock(symbol, "SMART", "USD")
    ib.qualifyContracts(contract)

    ticker = ib.reqMktData(contract)

    try:
        while True:

            ib.sleep(1)

            data = {
                "symbol": symbol,
                "bid": ticker.bid,
                "ask": ticker.ask,
                "last": ticker.last
            }

            await websocket.send_json(data)

    except Exception:
        await websocket.close()