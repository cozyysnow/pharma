import datetime
from sqlalchemy import Column, String, Text, DateTime
from backend.app.db.base import Base


class AppSetting(Base):
    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True, index=True)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)


class DatasetImport(Base):
    __tablename__ = "dataset_imports"

    import_id = Column(String(50), primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=True)
    row_count = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="SUCCESS")
    imported_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    details_json = Column(Text, nullable=True)
