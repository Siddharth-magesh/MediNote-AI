"""API v1 router configuration."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.patients import router as patients_router
from app.api.v1.recording import router as recording_router
from app.api.v1.extraction import router as extraction_router
from app.api.v1.reports import router as reports_router

# Main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth_router)
api_router.include_router(patients_router)
api_router.include_router(recording_router)
api_router.include_router(extraction_router)
api_router.include_router(reports_router)

# Additional routers will be added in later phases:
# api_router.include_router(visits_router)
