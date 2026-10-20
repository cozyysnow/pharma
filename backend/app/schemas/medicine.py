from typing import Optional
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.category import CategoryRead
from backend.app.schemas.supplier import SupplierRead


class MedicineBase(BaseModel):
    medicine_id: str
    generic_name: str
    display_name: str
    active_ingredients: Optional[str] = None
    strength: str
    dosage_form: str
    route: str = "Oral"
    category_id: str
    primary_supplier_id: str
    unit_of_measure: str = "strip"
    pack_size: int = 10
    storage_condition: str = "Room Temperature"
    unit_cost_inr: float = 0.0
    unit_price_inr: float = 0.0
    composition_status: str = "VERIFIED_STANDARD_REFERENCE"
    composition_note: Optional[str] = None
    is_active: bool = True


class MedicineCreate(MedicineBase):
    pass


class MedicineUpdate(BaseModel):
    generic_name: Optional[str] = None
    display_name: Optional[str] = None
    active_ingredients: Optional[str] = None
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    route: Optional[str] = None
    category_id: Optional[str] = None
    primary_supplier_id: Optional[str] = None
    unit_of_measure: Optional[str] = None
    pack_size: Optional[int] = None
    storage_condition: Optional[str] = None
    unit_cost_inr: Optional[float] = None
    unit_price_inr: Optional[float] = None
    composition_status: Optional[str] = None
    composition_note: Optional[str] = None
    is_active: Optional[bool] = None


class MedicineRead(MedicineBase):
    category: Optional[CategoryRead] = None
    primary_supplier: Optional[SupplierRead] = None

    model_config = ConfigDict(from_attributes=True)
