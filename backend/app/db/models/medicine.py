from sqlalchemy import Column, String, Float, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class Medicine(Base):
    __tablename__ = "medicines"

    medicine_id = Column(String(50), primary_key=True, index=True)
    generic_name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    active_ingredients = Column(String(255), nullable=True)
    strength = Column(String(100), nullable=False)
    dosage_form = Column(String(100), nullable=False)
    route = Column(String(50), nullable=False, default="Oral")
    category_id = Column(String(50), ForeignKey("categories.category_id"), nullable=False, index=True)
    primary_supplier_id = Column(String(50), ForeignKey("suppliers.supplier_id"), nullable=False, index=True)
    unit_of_measure = Column(String(50), nullable=False, default="strip")
    pack_size = Column(Integer, nullable=False, default=10)
    storage_condition = Column(String(100), nullable=False, default="Room Temperature")
    unit_cost_inr = Column(Float, nullable=False, default=0.0)
    unit_price_inr = Column(Float, nullable=False, default=0.0)
    composition_status = Column(String(100), nullable=False, default="VERIFIED_STANDARD_REFERENCE")
    composition_note = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    category = relationship("Category", back_populates="medicines")
    primary_supplier = relationship("Supplier", back_populates="medicines")
    inventory = relationship("InventoryCurrent", back_populates="medicine", uselist=False)
    transactions = relationship("Transaction", back_populates="medicine")

    def __repr__(self) -> str:
        return f"<Medicine {self.medicine_id}: {self.display_name}>"
