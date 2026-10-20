import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db
from backend.app.core.config import settings

router = APIRouter(tags=["System Health & Diagnostics"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check verifying API responsiveness and database connectivity."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if "unhealthy" not in db_status else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@router.get("/system/status")
def system_status(db: Session = Depends(get_db)):
    """Detailed operational status for dashboard diagnostics."""
    return {
        "status": "operational",
        "reference_date": "2025-12-31",
        "modules": {
            "authentication": "operational",
            "inventory_engine": "operational",
            "risk_classifier": "operational",
            "replenishment_service": "operational",
            "demand_forecasting_ml": "operational",
        },
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
