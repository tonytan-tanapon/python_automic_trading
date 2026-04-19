from fastapi import APIRouter, HTTPException
from app.services.ib_client import get_ib_connection_status, ib_call

router = APIRouter(prefix="/account", tags=["Account"])


@router.get("/connection")
def get_account_connection():
    return get_ib_connection_status()


@router.get("/")
def get_account():
    def _get_account(ib):
        summary = ib.accountSummary()
        result = {}

        for item in summary:
            result[item.tag] = item.value

        return result

    try:
        return ib_call(_get_account)
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
