from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.projects import router as projects_router
from app.api.routes.runs import router as runs_router
from app.api.routes.samples import router as samples_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(runs_router, prefix="/runs", tags=["runs"])
api_router.include_router(samples_router, prefix="/samples", tags=["samples"])
