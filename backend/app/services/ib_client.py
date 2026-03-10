from ib_insync import IB, util
from app.config import TWS_HOST, TWS_PORT, CLIENT_ID

# start asyncio loop
util.startLoop()

ib = IB()

def connect_ib():
    try:
        if not ib.isConnected():
            ib.connect(TWS_HOST, TWS_PORT, clientId=CLIENT_ID, timeout=5)
        return ib
    except Exception as e:
        raise ConnectionError(f"Could not connect to IB/TWS: {e}")

def disconnect_ib():
    if ib.isConnected():
        ib.disconnect()

def get_ib():
    return ib