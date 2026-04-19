from concurrent.futures import ThreadPoolExecutor

from ib_insync import IB
from app.config import TWS_HOST, TWS_PORT, CLIENT_ID

_ib = IB()
_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ib-client")


def _ensure_connection():
    try:
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
