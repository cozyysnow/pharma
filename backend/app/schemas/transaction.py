import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from backend.app.db.models.transaction import TransactionType
from backend.app.schemas.medicine import MedicineRead


class TransactionCreate(BaseModel):
    medicine_id: str
    transaction_type: TransactionType
    quantity: int
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class TransactionRead(BaseModel):
    id: str
    transaction_date: datetime.datetime
    medicine_id: str
    transaction_type: TransactionType
    quantity: int
    unit_price_inr: Optional[float] = None
    total_value_inr: Optional[float] = None
    stock_before: int
    stock_after: int
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    created_by: str
    medicine: Optional[MedicineRead] = None

    model_config = ConfigDict(from_attributes=True)


class TransactionSummary(BaseModel):
    total_transactions: int
    total_units_inflow: int
    total_units_outflow: int
    total_sales_value_inr: float
