"""API routers for CivicPulse AI."""

from app.routers.health import router as health_router
from app.routers.assets import router as assets_router
from app.routers.complaints import router as complaints_router

__all__ = [
    "health_router",
    "assets_router",
    "complaints_router",
]
