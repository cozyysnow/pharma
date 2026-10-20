import csv
import io
import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models.user import User
from backend.app.db.models.transaction import TransactionType
from backend.app.schemas.transaction import (
    TransactionRead,
    TransactionCreate,
    TransactionSummary,
)
from backend.app.schemas.common import PaginatedResponse
from backend.app.services.transaction_service import TransactionService
from backend.app.core.deps import get_current_user, require_manager_or_admin

router = APIRouter(prefix="/transactions", tags=["Transactions"])


class VoidPayload(BaseModel):
    reason: Optional[str] = "Administrative void"


@router.get("/summary", response_model=TransactionSummary)
def get_transactions_summary(
    db: Session = Depends(get_db),
):
    """Retrieve cumulative inventory movement metrics and sales volume."""
    return TransactionService.get_summary(db)


@router.get("/export")
def export_transactions_csv(
    medicine_id: Optional[str] = None,
    transaction_type: Optional[TransactionType] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Export transactions to CSV for accounting and audit compliance."""
    items, _ = TransactionService.list_transactions(
        db=db,
        medicine_id=medicine_id,
        transaction_type=transaction_type,
        search=search,
        page=1,
        page_size=10000,
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Transaction ID",
        "Date",
        "Medicine ID",
        "Medicine Name",
        "Type",
        "Quantity",
        "Unit Price (INR)",
        "Total Value (INR)",
        "Stock Before",
        "Stock After",
        "Reference Number",
        "Created By",
        "Notes",
    ])
    for tx in items:
        med_name = tx.medicine.display_name if tx.medicine else ""
        writer.writerow([
            tx.id,
            tx.transaction_date.isoformat() if tx.transaction_date else "",
            tx.medicine_id,
            med_name,
            tx.transaction_type.value if tx.transaction_type else "",
            tx.quantity,
            tx.unit_price_inr,
            tx.total_value_inr,
            tx.stock_before,
            tx.stock_after,
            tx.reference_number or "",
            tx.created_by or "",
            tx.notes or "",
        ])
    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions_export.csv"},
    )


@router.get("", response_model=PaginatedResponse[TransactionRead])
def list_transactions(
    medicine_id: Optional[str] = None,
    transaction_type: Optional[TransactionType] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List historical inventory movements with audit logs and medicine associations."""
    items, total = TransactionService.list_transactions(
        db=db,
        medicine_id=medicine_id,
        transaction_type=transaction_type,
        search=search,
        page=page,
        page_size=page_size,
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginatedResponse(
        data=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def record_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Record a stock movement (sale, receipt, adjustment, wastage). Strictly enforces non-negative stock."""
    return TransactionService.create_transaction(
        db=db,
        tx_in=payload,
        user_name=user.name or user.email,
    )


@router.post("/{transaction_id}/void", response_model=TransactionRead)
def void_transaction(
    transaction_id: str,
    payload: Optional[VoidPayload] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """Manager/Admin: Void a previous transaction with automatic compensating entry and inventory reversal."""
    reason = payload.reason if payload else "Administrative void"
    return TransactionService.void_transaction(
        db=db,
        transaction_id=transaction_id,
        user_name=user.name or user.email,
        reason=reason,
    )
