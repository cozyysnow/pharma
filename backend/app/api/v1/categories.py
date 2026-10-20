from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models.user import User
from backend.app.schemas.category import CategoryRead, CategoryCreate
from backend.app.services.category_service import CategoryService
from backend.app.core.deps import require_manager_or_admin

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryRead])
def get_categories(db: Session = Depends(get_db)):
    """Retrieve all pharmaceutical therapeutic categories."""
    return CategoryService.list_all(db)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """Manager/Admin: Register a new category."""
    return CategoryService.create(db, payload)
