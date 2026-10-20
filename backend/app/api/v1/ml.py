"""API endpoints for ML model training, evaluation runs, and activation."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.session import get_db, SessionLocal
from backend.app.db.models.user import User
from backend.app.db.models.forecast import MLRun
from backend.app.core.deps import require_manager_or_admin, require_admin
from backend.app.ml.registry import ModelRegistry
from backend.app.ml.train import MLTrainer

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


class TrainResponse(BaseModel):
    message: str
    status: str


class MLRunResponse(BaseModel):
    run_id: str
    model_name: str
    run_date: str
    horizon_days: int
    mae: float
    rmse: float
    wape: float
    selection_reason: Optional[str] = None
    is_active: bool


def _background_train():
    db = SessionLocal()
    try:
        MLTrainer.train_pipeline(db=db)
    finally:
        db.close()


@router.post("/train", response_model=TrainResponse)
def trigger_training(
    background_tasks: BackgroundTasks,
    user: User = Depends(require_manager_or_admin),
):
    """Manager/Admin: Launch asynchronous ML training, backtesting, and model selection pipeline."""
    background_tasks.add_task(_background_train)
    return {
        "message": "Model training pipeline triggered in background.",
        "status": "RUNNING",
    }


@router.get("/runs")
def list_ml_runs(
    db: Session = Depends(get_db),
):
    """List all recorded ML model training and backtesting runs."""
    db_runs = db.query(MLRun).order_by(MLRun.run_date.desc()).all()
    if db_runs:
        return [
            {
                "run_id": r.run_id,
                "model_name": r.model_name,
                "run_date": r.run_date.isoformat() if r.run_date else None,
                "horizon_days": r.horizon_days,
                "mae": r.mae,
                "rmse": r.rmse,
                "wape": r.wape,
                "selection_reason": r.selection_reason,
                "is_active": r.is_active,
            }
            for r in db_runs
        ]

    # Fallback to file-based model registry
    artifacts = ModelRegistry.list_artifacts()
    return [
        {
            "run_id": a["run_id"],
            "model_name": a["selected_model"],
            "run_date": a["saved_at"],
            "horizon_days": a["config"]["horizons"][-1],
            "mae": a["test_metrics"]["mae"],
            "rmse": a["test_metrics"]["rmse"],
            "wape": a["test_metrics"]["wape"],
            "selection_reason": a.get("selection_reason"),
            "is_active": idx == 0,
        }
        for idx, a in enumerate(artifacts)
    ]


@router.get("/runs/{run_id}")
def get_ml_run_details(
    run_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve full evaluation breakdown and parameters for a specific run."""
    try:
        _, meta = ModelRegistry.load_artifact(run_id)
        return meta
    except FileNotFoundError:
        run = db.query(MLRun).filter(MLRun.run_id == run_id).first()
        if not run:
            raise HTTPException(status_code=404, detail="ML run not found")
        return {
            "run_id": run.run_id,
            "selected_model": run.model_name,
            "test_metrics": {
                "mae": run.mae,
                "rmse": run.rmse,
                "wape": run.wape,
            },
            "selection_reason": run.selection_reason,
            "is_active": run.is_active,
        }


@router.post("/runs/{run_id}/activate")
def activate_ml_run(
    run_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """Manager/Admin: Set an ML run as the primary operational model."""
    run = db.query(MLRun).filter(MLRun.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="ML run not found")

    db.query(MLRun).update({MLRun.is_active: False})
    run.is_active = True
    db.commit()

    return {"message": f"Run {run_id} activated successfully.", "active_model": run.model_name}
