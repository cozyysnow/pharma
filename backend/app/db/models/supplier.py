from sqlalchemy import Column, String, Float, Integer, Boolean
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(String(50), primary_key=True, index=True)
    supplier_name = Column(String(255), nullable=False)
    supplier_type = Column(String(100), nullable=False, default="Wholesaler")
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    lead_time_mean_days = Column(Float, nullable=False, default=5.0)
    lead_time_sd_days = Column(Float, nullable=False, default=1.0)
    on_time_probability = Column(Float, nullable=False, default=0.90)
    full_fill_probability = Column(Float, nullable=False, default=0.95)
    payment_terms_days = Column(Integer, nullable=False, default=30)
    is_active = Column(Boolean, nullable=False, default=True)

    medicines = relationship("Medicine", back_populates="primary_supplier")

    def __repr__(self) -> str:
        return f"<Supplier {self.supplier_id}: {self.supplier_name}>"
