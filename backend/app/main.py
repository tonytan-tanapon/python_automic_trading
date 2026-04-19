from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import api_router
from app.services.auto_trading_service import auto_trading_engine

app = FastAPI(title="Auto Trading API")
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="frontend-assets")


@app.on_event("startup")
async def startup_event():
    init_db()
    await auto_trading_engine.startup()


@app.on_event("shutdown")
async def shutdown_event():
    await auto_trading_engine.shutdown()


@app.get("/")
def dashboard():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "running"}
