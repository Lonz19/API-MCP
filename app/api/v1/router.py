from fastapi import APIRouter
from app.api.v1.summarize import router as summarize_router
from app.api.v1.gemini import router as gemini_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(summarize_router)
v1_router.include_router(gemini_router)
