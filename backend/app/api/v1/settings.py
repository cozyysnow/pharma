from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models.user import User
from backend.app.schemas.settings import SettingRead, SettingUpdate
from backend.app.services.settings_service import SettingsService
from backend.app.core.deps import require_admin
from backend.app.core.errors import NotFoundException

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=List[SettingRead])
def list_settings(
    db: Session = Depends(get_db),
):
    """Retrieve all configurable system parameters."""
    return SettingsService.list_all(db)


@router.get("/{key}", response_model=SettingRead)
def get_setting(
    key: str,
    db: Session = Depends(get_db),
):
    """Get single configuration parameter by key."""
    s = SettingsService.get_by_key(db, key)
    if not s:
        raise NotFoundException("Setting", key)
    return s


@router.patch("/{key}", response_model=SettingRead)
def update_setting(
    key: str,
    payload: SettingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """Admin only: Update application setting."""
    return SettingsService.update_setting(db, key, payload)
