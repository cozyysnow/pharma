import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class InventoryCurrent(Base):
    __tablename__ = "inventory_current"

    medicine_id = Column(String(50), ForeignKey("medicines.medicine_id"), primary_key=True, index=True)
    opening_stock = Column(Integer, nullable=False, default=0)
    closing_stock = Column(Integer, nullable=False, default=0)
    units_received_today = Column(Integer, nullable=False, default=0)
    units_sold_today = Column(Integer, nullable=False, default=0)
    units_adjusted_today = Column(Integer, nullable=False, default=0)
    wastage_units = Column(Integer, nullable=False, default=0)
    units_ordered_today = Column(Integer, nullable=False, default=0)
    on_order_units = Column(Integer, nullable=False, default=0)
    reorder_point = Column(Integer, nullable=False, default=100)
    order_up_to_level = Column(Integer, nullable=False, default=500)
    days_of_cover = Column(Float, nullable=False, default=0.0)
    stock_status = Column(String(50), nullable=False, default="IN_STOCK")  # IN_STOCK, LOW_STOCK, OUT_OF_STOCK, OVERSTOCKED
    safety_stock = Column(Integer, nullable=False, default=50)
    moq = Column(Integer, nullable=False, default=50)
    expected_daily_demand = Column(Float, nullable=False, default=10.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    medicine = relationship("Medicine", back_populates="inventory")

    def __repr__(self) -> str:
        return f"<InventoryCurrent {self.medicine_id}: stock={self.closing_stock} status={self.stock_status}>"
