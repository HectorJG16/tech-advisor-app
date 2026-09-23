from fastapi import APIRouter

from app.routes.feedback import router as feedback_router
from app.routes.intake import router as intake_router
from app.routes.recommend import router as recommend_router
from app.routes.sessions import router as sessions_router

api_router = APIRouter()
api_router.include_router(sessions_router)
api_router.include_router(intake_router)
api_router.include_router(recommend_router)
api_router.include_router(feedback_router)
