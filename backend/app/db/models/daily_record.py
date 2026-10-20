from sqlalchemy import Column, String, Integer, Float, Boolean, Date, ForeignKey, Index
from backend.app.db.base import Base


class DailyRecord(Base):
    __tablename__ = "daily_records"

    record_id = Column(String(50), primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    medicine_id = Column(String(50), ForeignKey("medicines.medicine_id"), nullable=False, index=True)
    category_id = Column(String(50), nullable=False)
    supplier_id = Column(String(50), nullable=False)
    closing_stock = Column(Integer, nullable=False)
    on_order_units = Column(Integer, nullable=False, default=0)
    reorder_point = Column(Integer, nullable=False, default=100)
    units_demanded = Column(Integer, nullable=False, default=0)
    units_sold = Column(Integer, nullable=False, default=0)
    sales_7d_avg = Column(Float, nullable=False, default=0.0)
    sales_30d_avg = Column(Float, nullable=False, default=0.0)
    days_of_cover = Column(Float, nullable=False, default=0.0)
    stock_position_cover_days = Column(Float, nullable=False, default=0.0)
    days_since_last_receipt = Column(Integer, nullable=False, default=0)
    stockout_days_last_30d = Column(Integer, nullable=False, default=0)
    supplier_lead_time_mean_days = Column(Float, nullable=False, default=5.0)
    supplier_full_fill_probability = Column(Float, nullable=False, default=0.95)
    supplier_disruption_active = Column(Boolean, nullable=False, default=False)
    unit_price_inr = Column(Float, nullable=False, default=0.0)
    stockout_today = Column(Boolean, nullable=False, default=False)
    stockout_next_7d = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index("ix_daily_records_med_date", "medicine_id", "date", unique=True),
    )

    def __repr__(self) -> str:
        return f"<DailyRecord {self.medicine_id} {self.date}: demand={self.units_demanded} stock={self.closing_stock}>"
