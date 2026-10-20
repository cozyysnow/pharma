import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey
from backend.app.db.base import Base


class ReplenishmentRecommendation(Base):
    __tablename__ = "replenishment_recommendations"

    recommendation_id = Column(String(50), primary_key=True, index=True)
    medicine_id = Column(String(50), ForeignKey("medicines.medicine_id"), nullable=False, index=True)
    supplier_id = Column(String(50), ForeignKey("suppliers.supplier_id"), nullable=False, index=True)
    current_stock = Column(Integer, nullable=False)
    open_order_qty = Column(Integer, nullable=False, default=0)
    required_stock = Column(Integer, nullable=False)
    lead_time_days = Column(Float, nullable=False)
    moq_applied = Column(Integer, nullable=False)
    recommended_order_quantity = Column(Integer, nullable=False)
    is_urgent = Column(Boolean, nullable=False, default=False)
    status = Column(String(50), nullable=False, default="PENDING")  # PENDING, ACCEPTED, ORDERED, DISMISSED
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    ordered_at = Column(DateTime, nullable=True)
    dismissed_at = Column(DateTime, nullable=True)
    accepted_by = Column(String(100), nullable=True)
    dismissed_by = Column(String(100), nullable=True)
    dismiss_reason = Column(Text, nullable=True)
    po_reference = Column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"<ReplenishmentRecommendation {self.recommendation_id} {self.medicine_id}: qty={self.recommended_order_quantity} status={self.status}>"
