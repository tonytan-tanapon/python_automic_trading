from ib_insync import IB
from app.config import TWS_HOST, TWS_PORT, CLIENT_ID

ib = IB()

def connect_ib():
    ib.connect(TWS_HOST, TWS_PORT, clientId=CLIENT_ID)
    return ib