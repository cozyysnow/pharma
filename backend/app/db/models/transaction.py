import datetime
import enum
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class TransactionType(str, enum.Enum):
    SALE = "SALE"
    RECEIPT = "RECEIPT"
    ADJUSTMENT_POSITIVE = "ADJUSTMENT_POSITIVE"
    ADJUSTMENT_NEGATIVE = "ADJUSTMENT_NEGATIVE"
    WASTAGE = "WASTAGE"
    RETURN_FROM_PATIENT = "RETURN_FROM_PATIENT"
    TRANSFER_OUT = "TRANSFER_OUT"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(50), primary_key=True, index=True)
    transaction_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    medicine_id = Column(String(50), ForeignKey("medicines.medicine_id"), nullable=False, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price_inr = Column(Float, nullable=True)
    total_value_inr = Column(Float, nullable=True)
    stock_before = Column(Integer, nullable=False)
    stock_after = Column(Integer, nullable=False)
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=False, default="System")

    medicine = relationship("Medicine", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction {self.id} {self.transaction_type} {self.medicine_id}: qty={self.quantity}>"
