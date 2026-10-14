"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "CivicPulse AI Backend",
        "version": "0.1.0"
    }

@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "CivicPulse AI Backend API",
        "version": "0.1.0",
        "docs": "/docs"
    }
