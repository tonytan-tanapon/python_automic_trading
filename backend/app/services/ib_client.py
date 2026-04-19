import asyncio
from concurrent.futures import ThreadPoolExecutor

from ib_insync import IB
from app.config import TWS_HOST, TWS_PORT, CLIENT_ID

_ib = IB()
_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ib-client")


def _ensure_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def _ensure_connection():
    try:
        _ensure_event_loop()
        if not _ib.isConnected():
            _ib.connect(TWS_HOST, TWS_PORT, clientId=CLIENT_ID, timeout=5)
        return _ib
    except Exception as e:
        raise ConnectionError(f"Could not connect to IB/TWS: {e}")


def ib_call(fn):
    """
    Run every IB request on one dedicated thread.
    This avoids event-loop conflicts with FastAPI/uvicorn.
    """
    return _executor.submit(lambda: fn(_ensure_connection())).result()


def run_ib_call(callback):
    return ib_call(callback)


def disconnect_ib():
    def _disconnect(ib):
        if ib.isConnected():
            ib.disconnect()

    return ib_call(_disconnect)


def get_ib_connection_status():
    def _status():
        _ensure_event_loop()

        try:
            if not _ib.isConnected():
                _ib.connect(TWS_HOST, TWS_PORT, clientId=CLIENT_ID, timeout=5)

            return {
                "connected": _ib.isConnected(),
                "host": TWS_HOST,
                "port": TWS_PORT,
                "client_id": CLIENT_ID,
                "message": "Connected to IB/TWS" if _ib.isConnected() else "Not connected",
            }
        except Exception as e:
            return {
                "connected": False,
                "host": TWS_HOST,
                "port": TWS_PORT,
                "client_id": CLIENT_ID,
                "message": f"Could not connect to IB/TWS: {e}",
            }

    return _executor.submit(_status).result()
