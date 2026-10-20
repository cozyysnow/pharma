from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models.user import User
from backend.app.schemas.user import UserRead, UserCreate, UserUpdate
from backend.app.schemas.common import PaginatedResponse
from backend.app.services.user_service import UserService
from backend.app.core.deps import require_admin

router = APIRouter(prefix="/users", tags=["User Administration"])


@router.get("", response_model=PaginatedResponse[UserRead])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Admin-only: List registered system users with pagination."""
    skip = (page - 1) * page_size
    users = UserService.list_all(db, skip=skip, limit=page_size)
    total = UserService.count(db)
    return PaginatedResponse(
        data=[UserRead.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if page_size > 0 else 1,
    )


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Admin-only: Create a new system user with assigned role."""
    return UserService.create(db, payload)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Admin-only: Modify role, status, or details of a user."""
    return UserService.update(db, user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Admin-only: Soft-deactivate a user account."""
    UserService.deactivate(db, user_id)
    return {"message": f"User {user_id} has been deactivated."}
