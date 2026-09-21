"""Unified API v1 router."""
from fastapi import APIRouter

from backend.app.api.v1.advisors import router as advisors_router
from backend.app.api.v1.analytics import router as analytics_router
from backend.app.api.v1.courses import router as courses_router
from backend.app.api.v1.matching import router as matching_router
from backend.app.api.v1.system import router as system_router
from backend.app.api.v1.theses import router as theses_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(advisors_router)
v1_router.include_router(theses_router)
v1_router.include_router(courses_router)
v1_router.include_router(matching_router)
v1_router.include_router(analytics_router)
v1_router.include_router(system_router)
