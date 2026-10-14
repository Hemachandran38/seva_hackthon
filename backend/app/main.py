"""
CivicPulse AI Backend - Main Application

A FastAPI application for managing infrastructure maintenance issues.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import health_router, assets_router, complaints_router
from app.routers.priority import router as priority_router
from app.routers.dashboard import router as dashboard_router

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting CivicPulse AI Backend")
    init_db()
    yield
    # Shutdown
    logger.info("Shutting down CivicPulse AI Backend")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for CivicPulse AI infrastructure maintenance platform",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(assets_router)
app.include_router(complaints_router)
app.include_router(priority_router)
app.include_router(dashboard_router)

logger.info(f"CivicPulse AI Backend initialized - {settings.app_name} v{settings.app_version}")
