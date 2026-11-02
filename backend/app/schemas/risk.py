from typing import Optional, List, Union
import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.medicine import MedicineRead


class RiskFactor(BaseModel):
    factor: str
    value: Union[str, float, int]
    contribution: float
    explanation: str


class RiskResultRead(BaseModel):
    id: str
    risk_id: str
    medicine_id: str
    calculated_at: datetime.datetime
    computed_at: datetime.datetime
    risk_score: int
    risk_level: str
    expected_daily_demand: float
    avg_daily_demand: float
    stock_coverage_days: float
    days_of_cover: float
    days_until_stockout: Optional[float] = None
    lead_time_days: float
    lead_time_demand: float
    safety_stock: int
    required_stock: int
    reorder_point: int
    shortfall: int
    stockout_probability_7d: float
    stockout_probability_14d: float
    stockout_probability_30d: float
    explanation: str
    factors: List[RiskFactor] = []
    medicine: Optional[MedicineRead] = None

    model_config = ConfigDict(from_attributes=True)


class CalculationChainRead(BaseModel):
    medicine_id: str
    expected_daily_demand: float
    closing_stock: int
    coverage_days: float
    lead_time_days: float
    lead_time_demand: float
    safety_stock: int
    required_stock: int
    reorder_point: int
    shortfall: int
    risk_score: int
    risk_level: str
    explanation: str
    factors: List[RiskFactor] = []


class RiskRunResponse(BaseModel):
    run_id: str
    status: str
    medicines_evaluated: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    computed_at: datetime.datetime
