from typing import Optional
from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    category_id: str
    category_name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
