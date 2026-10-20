import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SettingRead(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class SettingUpdate(BaseModel):
    value: str
    description: Optional[str] = None
