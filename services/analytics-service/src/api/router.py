from fastapi import APIRouter

from src.api.routes import stats

api_router = APIRouter()

api_router.include_router(stats.router, prefix='/stats', tags=['stats'])
