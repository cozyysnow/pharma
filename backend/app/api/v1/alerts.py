from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.alert import (
    AlertRead,
    BulkAcknowledgeRequest,
    BulkAcknowledgeResponse,
    UnreadCountResponse,
)
from backend.app.services.alert_service import AlertService, AlertEngine
from backend.app.core.deps import get_current_user
from backend.app.core.errors import NotFoundException

router = APIRouter(prefix="/alerts", tags=["Alerts & Notifications"])


@router.get("", response_model=List[AlertRead])
def list_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
    medicine_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Retrieve system alerts with optional filtering."""
    return AlertService.list_alerts(
        db=db,
        status=status,
        severity=severity,
        alert_type=alert_type,
        medicine_id=medicine_id,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
    db: Session = Depends(get_db),
):
    """Returns number of unread alerts for the header notification bell."""
    count = AlertService.get_unread_count(db)
    return UnreadCountResponse(unread_count=count)


@router.post("/evaluate", status_code=status.HTTP_200_OK)
def trigger_alert_evaluation(
    db: Session = Depends(get_db),
):
    """Manually run alert evaluation engine across current risk and inventory states."""
    return AlertEngine.evaluate_system_alerts(db)


@router.post("/bulk-acknowledge", response_model=BulkAcknowledgeResponse)
def bulk_acknowledge_alerts(
    payload: BulkAcknowledgeRequest,
    db: Session = Depends(get_db),
):
    """Bulk-acknowledges a list of alert IDs."""
    count = AlertService.bulk_acknowledge(db, payload.ids)
    return BulkAcknowledgeResponse(acknowledged_count=count)


@router.post("/{alert_id}/acknowledge", response_model=AlertRead)
def acknowledge_alert(
    alert_id: str,
    db: Session = Depends(get_db),
):
    """Acknowledge single alert."""
    result = AlertService.acknowledge(db, alert_id)
    if not result:
        raise NotFoundException("Alert", alert_id)
    return result


@router.post("/{alert_id}/resolve", response_model=AlertRead)
def resolve_alert(
    alert_id: str,
    db: Session = Depends(get_db),
):
    """Mark alert as resolved."""
    result = AlertService.resolve(db, alert_id)
    if not result:
        raise NotFoundException("Alert", alert_id)
    return result


@router.post("/{alert_id}/dismiss", response_model=AlertRead)
def dismiss_alert(
    alert_id: str,
    db: Session = Depends(get_db),
):
    """Dismiss single alert."""
    result = AlertService.dismiss(db, alert_id)
    if not result:
        raise NotFoundException("Alert", alert_id)
    return result

