from typing import Optional
import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.medicine import MedicineRead
from backend.app.schemas.supplier import SupplierRead


class RecommendationRead(BaseModel):
    id: str
    recommendation_id: str
    medicine_id: str
    supplier_id: str
    current_stock: int
    open_order_qty: int
    required_stock: int
    lead_time_days: float
    moq_applied: int
    recommended_order_quantity: int
    recommended_quantity: int
    estimated_cost_inr: float
    urgency_level: str
    is_urgent: bool
    reorder_point: int
    days_of_cover: float
    rationale: str
    status: str
    created_at: datetime.datetime
    generated_at: datetime.datetime
    accepted_at: Optional[datetime.datetime] = None
    ordered_at: Optional[datetime.datetime] = None
    dismissed_at: Optional[datetime.datetime] = None
    accepted_by: Optional[str] = None
    dismissed_by: Optional[str] = None
    dismiss_reason: Optional[str] = None
    po_reference: Optional[str] = None
    medicine: Optional[MedicineRead] = None
    supplier: Optional[SupplierRead] = None

    model_config = ConfigDict(from_attributes=True)


class DismissRecommendationRequest(BaseModel):
    reason: str
    by: Optional[str] = None


class AcceptRecommendationRequest(BaseModel):
    by: Optional[str] = None

