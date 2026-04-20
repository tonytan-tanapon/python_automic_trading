import asyncio
from concurrent.futures import ThreadPoolExecutor

from ib_insync import IB
from app.config import TWS_HOST, TWS_PORT, CLIENT_ID

# สร้าง client กลาง สำหรับการเชื่อมต่อกับ IB/TWS และใช้ thread pool เพื่อจัดการกับการเรียกใช้ client ใน thread แยกต่างหาก
_ib = IB()

# สร้าง thread กลาง สำหรับการเรียกใช้ IB client เพื่อหลีกเลี่ยงปัญหา event loop กับ FastAPI/uvicorn
_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ib-client")


def _ensure_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

# คำสั่ง connect จริงๆ 
# _ib.connect(TWS_HOST, TWS_PORT, clientId=CLIENT_ID, timeout=5)
def _ensure_connection():
    try:
        _ensure_event_loop()
        if not _ib.isConnected():
            _ib.connect(TWS_HOST, TWS_PORT, clientId=CLIENT_ID, timeout=5)
        return _ib
    except Exception as e:
        raise ConnectionError(f"Could not connect to IB/TWS: {e}")

# เรียกใช้ฟังก์ชันนี้เพื่อเรียกใช้คำสั่งต่างๆ กับ IB client ใน thread แยกต่างหาก
# ตัวอย่างเช่น: ib_call(lambda ib: ib.accountSummary())

def ib_call(fn):
    """
    Run every IB request on one dedicated thread.
    This avoids event-loop conflicts with FastAPI/uvicorn.
    """
    return _executor.submit(lambda: fn(_ensure_connection())).result()


def connect_ib():
    def _connect():
        _ensure_connection()
        return {
            "connected": _ib.isConnected(),
            "host": TWS_HOST,
            "port": TWS_PORT,
            "client_id": CLIENT_ID,
            "message": "Connected to IB/TWS" if _ib.isConnected() else "Not connected",
        }

    return _executor.submit(_connect).result()

# คำสั่ง disconnect จริงๆ 
# _ib.disconnect()
def disconnect_ib():
    def _disconnect():
        _ensure_event_loop()
        if _ib.isConnected():
            _ib.disconnect()

        return {
            "connected": _ib.isConnected(),
            "host": TWS_HOST,
            "port": TWS_PORT,
            "client_id": CLIENT_ID,
            "message": "Disconnected from IB/TWS" if not _ib.isConnected() else "Still connected",
        }

    return _executor.submit(_disconnect).result()


def reconnect_ib():
    def _reconnect():
        _ensure_event_loop()
        if _ib.isConnected():
            _ib.disconnect()

        _ib.connect(TWS_HOST, TWS_PORT, clientId=CLIENT_ID, timeout=5)
        return {
            "connected": _ib.isConnected(),
            "host": TWS_HOST,
            "port": TWS_PORT,
            "client_id": CLIENT_ID,
            "message": "Reconnected to IB/TWS" if _ib.isConnected() else "Reconnect failed",
        }

    try:
        return _executor.submit(_reconnect).result()
    except Exception as e:
        raise ConnectionError(f"Could not reconnect to IB/TWS: {e}")


def get_ib_health():
    status = get_ib_connection_status()
    return {
        "ok": status["connected"],
        "service": "tws",
        "connected": status["connected"],
        "host": status["host"],
        "port": status["port"],
        "client_id": status["client_id"],
        "message": status["message"],
    }


def get_ib_connection_status():
    def _status():
        _ensure_event_loop()

        connected = _ib.isConnected()
        return {
            "connected": connected,
            "host": TWS_HOST,
            "port": TWS_PORT,
            "client_id": CLIENT_ID,
            "message": "Connected to IB/TWS" if connected else "Not connected",
        }

    return _executor.submit(_status).result()
