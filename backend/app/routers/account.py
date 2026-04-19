from fastapi import APIRouter
from app.services.ib_client import ib_call

router = APIRouter(prefix="/account", tags=["Account"])


@router.get("/")
def get_account():
    def _get_account(ib):
        summary = ib.accountSummary()
        result = {}

        for item in summary:
            result[item.tag] = item.value

        return result

    return ib_call(_get_account)
