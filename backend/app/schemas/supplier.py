from typing import Optional
from pydantic import BaseModel, ConfigDict


class SupplierBase(BaseModel):
    supplier_id: str
    supplier_name: str
    supplier_type: str = "Wholesaler"
    city: str
    state: str
    lead_time_mean_days: float = 5.0
    lead_time_sd_days: float = 1.0
    on_time_probability: float = 0.90
    full_fill_probability: float = 0.95
    payment_terms_days: int = 30
    is_active: bool = True


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    supplier_name: Optional[str] = None
    supplier_type: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    lead_time_mean_days: Optional[float] = None
    lead_time_sd_days: Optional[float] = None
    on_time_probability: Optional[float] = None
    full_fill_probability: Optional[float] = None
    payment_terms_days: Optional[int] = None
    is_active: Optional[bool] = None


class SupplierRead(SupplierBase):
    model_config = ConfigDict(from_attributes=True)
