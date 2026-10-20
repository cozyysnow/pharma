import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from backend.app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(String(50), primary_key=True, index=True)
    medicine_id = Column(String(50), ForeignKey("medicines.medicine_id"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True)  # HIGH_RISK, LOW_STOCK, REPLENISHMENT_REQUIRED, DEMAND_SPIKE, FORECAST_DEVIATION
    severity = Column(String(50), nullable=False, index=True)    # CRITICAL, WARNING, INFO
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="UNREAD", index=True)  # UNREAD, ACKNOWLEDGED, RESOLVED, DISMISSED
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(100), nullable=True)
    resolved_by = Column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"<Alert {self.alert_id} {self.alert_type} {self.severity} status={self.status}>"
