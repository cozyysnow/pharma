from typing import Optional, List
import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.medicine import MedicineRead


class AlertBase(BaseModel):
    alert_type: str
    severity: str
    title: str
    message: str
    medicine_id: Optional[str] = None


class AlertRead(BaseModel):
    id: str
    alert_id: str
    medicine_id: Optional[str] = None
    alert_type: str
    severity: str
    title: str
    message: str
    status: str
    created_at: datetime.datetime
    acknowledged_at: Optional[datetime.datetime] = None
    resolved_at: Optional[datetime.datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    medicine: Optional[MedicineRead] = None

    model_config = ConfigDict(from_attributes=True)


class BulkAcknowledgeRequest(BaseModel):
    ids: List[str]


class BulkAcknowledgeResponse(BaseModel):
    acknowledged_count: int


class UnreadCountResponse(BaseModel):
    unread_count: int
