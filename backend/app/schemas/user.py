import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from backend.app.db.models.user import UserRole


class UserBase(BaseModel):
    email: str
    name: str
    role: UserRole = UserRole.PHARMACY_STAFF
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserRead(UserBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
