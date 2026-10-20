from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.db.models.category import Category
from backend.app.schemas.category import CategoryCreate


class CategoryService:
    @staticmethod
    def list_all(db: Session) -> List[Category]:
        return db.query(Category).order_by(Category.category_name).all()

    @staticmethod
    def get_by_id(db: Session, category_id: str) -> Optional[Category]:
        return db.query(Category).filter(Category.category_id == category_id).first()

    @staticmethod
    def create(db: Session, cat_in: CategoryCreate) -> Category:
        cat = Category(
            category_id=cat_in.category_id,
            category_name=cat_in.category_name,
            description=cat_in.description,
        )
        db.add(cat)
        db.commit()
        db.refresh(cat)
        return cat
