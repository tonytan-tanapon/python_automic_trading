import os
from dotenv import load_dotenv

load_dotenv()

TWS_HOST = os.getenv("TWS_HOST", "127.0.0.1")
TWS_PORT = int(os.getenv("TWS_PORT", 7497))
CLIENT_ID = int(os.getenv("CLIENT_ID", 1))
TRADING_MODE = os.getenv("TRADING_MODE", "paper")