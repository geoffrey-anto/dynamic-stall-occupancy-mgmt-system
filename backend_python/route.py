from fastapi import APIRouter
from routes.health import health_router
from routes.project import project_router

main_router = APIRouter()

main_router.include_router(health_router, prefix="/health", tags=["health"])
main_router.include_router(project_router, prefix="/project", tags=["project"])
