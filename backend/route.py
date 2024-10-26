from fastapi import APIRouter
from routes.health import health_router

main_router = APIRouter()

main_router.include_router(health_router, prefix="/health", tags=["health"])
