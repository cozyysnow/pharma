import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey
from backend.app.db.base import Base


class RiskResult(Base):
    __tablename__ = "risk_results"

    risk_id = Column(String(50), primary_key=True, index=True)
    medicine_id = Column(String(50), ForeignKey("medicines.medicine_id"), nullable=False, index=True)
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    risk_score = Column(Integer, nullable=False, default=0)
    risk_level = Column(String(50), nullable=False, default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL
    expected_daily_demand = Column(Float, nullable=False)
    stock_coverage_days = Column(Float, nullable=False)
    lead_time_days = Column(Float, nullable=False)
    safety_stock = Column(Integer, nullable=False)
    required_stock = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=False)
    factors_json = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<RiskResult {self.medicine_id}: score={self.risk_score} level={self.risk_level}>"
