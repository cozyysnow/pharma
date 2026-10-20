from typing import Generic, List, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[Any] = None
