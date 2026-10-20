from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(String(50), primary_key=True, index=True)
    category_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    medicines = relationship("Medicine", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category {self.category_id}: {self.category_name}>"
