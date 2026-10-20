from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.db.models.app_settings import AppSetting
from backend.app.schemas.settings import SettingUpdate
from backend.app.core.errors import NotFoundException


class SettingsService:
    @staticmethod
    def list_all(db: Session) -> List[AppSetting]:
        return db.query(AppSetting).order_by(AppSetting.key).all()

    @staticmethod
    def get_by_key(db: Session, key: str) -> Optional[AppSetting]:
        return db.query(AppSetting).filter(AppSetting.key == key).first()

    @staticmethod
    def update_setting(db: Session, key: str, setting_in: SettingUpdate) -> AppSetting:
        setting = SettingsService.get_by_key(db, key)
        if not setting:
            setting = AppSetting(
                key=key,
                value=setting_in.value,
                description=setting_in.description,
            )
            db.add(setting)
        else:
            setting.value = setting_in.value
            if setting_in.description:
                setting.description = setting_in.description

        db.commit()
        db.refresh(setting)
        return setting
