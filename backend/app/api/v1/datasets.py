from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models.user import User
from backend.app.services.dataset_service import DatasetService
from backend.app.dataset.validators import DatasetValidationReport
from backend.app.core.deps import require_manager_or_admin

router = APIRouter(prefix="/datasets", tags=["Datasets"])


class ImportPayload(BaseModel):
    force_reload: bool = False


@router.get("/status")
def get_dataset_status(
    db: Session = Depends(get_db),
):
    """Get raw dataset files detection and database population status."""
    return DatasetService.get_dataset_status(db)


@router.get("/preview")
def preview_dataset_file(
    filename: str = Query("stockout_prediction_dataset.csv", description="CSV filename in data/raw"),
    limit: int = Query(10, ge=1, le=100),
):
    """Preview first N rows, columns, and data types of a raw CSV file."""
    return DatasetService.preview_file(filename=filename, limit=limit)


@router.post("/validate", response_model=DatasetValidationReport)
def validate_dataset():
    """Run full schema verification and runtime quality validation rules across dataset pack."""
    return DatasetService.validate_dataset()


@router.post("/import")
def import_dataset(
    payload: Optional[ImportPayload] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """Manager/Admin: Ingest all categories, suppliers, medicines, and 155,210 daily records into database."""
    force_reload = payload.force_reload if payload else False
    result = DatasetService.run_import(db=db, force_reload=force_reload)
    return result.to_dict()


@router.get("/statistics")
def get_dataset_statistics(
    db: Session = Depends(get_db),
):
    """Retrieve aggregate dataset dimensions, date ranges, and stock-out prevalence."""
    return DatasetService.get_statistics(db)
