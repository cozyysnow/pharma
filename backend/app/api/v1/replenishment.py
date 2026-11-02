import csv
import io
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.replenishment import (
    RecommendationRead,
    DismissRecommendationRequest,
    AcceptRecommendationRequest,
)
from backend.app.services.replenishment_service import ReplenishmentService

router = APIRouter(prefix="/replenishment", tags=["Replenishment Recommendations"])


@router.get("", response_model=List[RecommendationRead])
def list_recommendations(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Retrieve replenishment recommendations filtered by status."""
    return ReplenishmentService.list_recommendations(db, status=status)


@router.post("/generate", status_code=status.HTTP_200_OK)
def trigger_replenishment_generation(
    db: Session = Depends(get_db),
):
    """Regenerates replenishment recommendations from latest inventory positions."""
    return ReplenishmentService.generate_recommendations(db)


@router.post("/{recommendation_id}/accept", response_model=RecommendationRead)
def accept_recommendation(
    recommendation_id: str,
    payload: Optional[AcceptRecommendationRequest] = None,
    db: Session = Depends(get_db),
):
    """Manager: Accept a replenishment recommendation."""
    user_name = payload.by if payload and payload.by else "Authorized Manager"
    return ReplenishmentService.accept(db, recommendation_id, by=user_name)


@router.post("/{recommendation_id}/order-placed", response_model=RecommendationRead)
def mark_order_placed(
    recommendation_id: str,
    db: Session = Depends(get_db),
):
    """Manager: Confirm external purchase order placed. Updates open_order_qty in inventory."""
    return ReplenishmentService.order_placed(db, recommendation_id)


@router.post("/{recommendation_id}/dismiss", response_model=RecommendationRead)
def dismiss_recommendation(
    recommendation_id: str,
    payload: DismissRecommendationRequest,
    db: Session = Depends(get_db),
):
    """Manager: Dismiss a replenishment recommendation with required reason."""
    user_name = payload.by or "Authorized Manager"
    return ReplenishmentService.dismiss(db, recommendation_id, reason=payload.reason, by=user_name)


@router.get("/export")
def export_replenishment_csv(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Exports replenishment recommendations to CSV."""
    recs = ReplenishmentService.list_recommendations(db, status=status)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID",
        "Medicine ID",
        "Medicine Name",
        "Supplier",
        "Recommended Qty",
        "Current Stock",
        "Required Stock",
        "Lead Time Days",
        "Urgency",
        "Status",
    ])
    for r in recs:
        med = r.get("medicine")
        sup = r.get("supplier")
        writer.writerow([
            r["id"],
            r["medicine_id"],
            med.display_name if med else "",
            sup.supplier_name if sup else "",
            r["recommended_quantity"],
            r["current_stock"],
            r["required_stock"],
            r["lead_time_days"],
            "URGENT" if r["is_urgent"] else "STANDARD",
            r["status"],
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=replenishment_recommendations.csv"},
    )

