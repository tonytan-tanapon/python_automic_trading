from fastapi import APIRouter
from app.services.ib_client import connect_ib

router = APIRouter(prefix="/account", tags=["Account"])

@router.get("/")
def get_account():
    ib = connect_ib()
    summary = ib.accountSummary()

    result = {}

    for item in summary:
        result[item.tag] = item.value

    return result