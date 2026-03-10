import os
from dotenv import load_dotenv

load_dotenv()

TWS_HOST = os.getenv("TWS_HOST")
TWS_PORT = int(os.getenv("TWS_PORT"))
CLIENT_ID = int(os.getenv("TWS_CLIENT_ID"))