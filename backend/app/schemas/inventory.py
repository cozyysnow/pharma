import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.medicine import MedicineRead


class InventoryItemBase(BaseModel):
    medicine_id: str
    opening_stock: int = 0
    closing_stock: int = 0
    units_received_today: int = 0
    units_sold_today: int = 0
    units_adjusted_today: int = 0
    wastage_units: int = 0
    units_ordered_today: int = 0
    on_order_units: int = 0
    reorder_point: int = 100
    order_up_to_level: int = 500
    days_of_cover: float = 0.0
    stock_status: str = "IN_STOCK"
    safety_stock: int = 50
    moq: int = 50
    expected_daily_demand: float = 10.0


class InventoryParamsUpdate(BaseModel):
    reorder_point: Optional[int] = None
    order_up_to_level: Optional[int] = None
    safety_stock: Optional[int] = None
    moq: Optional[int] = None


class InventoryItemRead(InventoryItemBase):
    updated_at: datetime.datetime
    medicine: Optional[MedicineRead] = None

    model_config = ConfigDict(from_attributes=True)


class InventorySummary(BaseModel):
    total_skus: int
    total_units_in_stock: int
    stockout_count: int
    low_stock_count: int
    adequate_stock_count: int
    overstocked_count: int
    total_stock_value_cost_inr: float
    total_stock_value_retail_inr: float
