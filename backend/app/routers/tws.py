from fastapi import APIRouter, HTTPException

from app.services.ib_client import (
    connect_ib,
    disconnect_ib,
    get_ib_connection_status,
    get_ib_health,
    reconnect_ib,
)

router = APIRouter(prefix="/tws", tags=["TWS"])


@router.get("/connection")
def get_tws_connection():
    return get_ib_connection_status()


@router.get("/health")
def get_tws_health():
    return get_ib_health()


@router.post("/connect")
def connect_tws():
    try:
        return connect_ib()
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@router.post("/disconnect")
def disconnect_tws():
    return disconnect_ib()


@router.post("/reconnect")
def reconnect_tws():
    try:
        return reconnect_ib()
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
