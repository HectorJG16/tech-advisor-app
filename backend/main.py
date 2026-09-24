from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(BACKEND))

import lightgbm as lgb  # noqa: F401

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.cache.redis_cache import redis_health
from app.routes import api_router
from schemas import HealthResponse


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        from app.ml.inference import get_ranker_artifact

        get_ranker_artifact()
    except FileNotFoundError:
        pass
    yield


app = FastAPI(title="Tech Advisor API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", redis=redis_health())


app.include_router(api_router)
