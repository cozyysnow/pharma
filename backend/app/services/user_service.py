from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.db.models.user import User, UserRole
from backend.app.schemas.user import UserCreate, UserUpdate
from backend.app.core.security import get_password_hash
from backend.app.core.errors import ConflictException, NotFoundException


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower()).first()

    @staticmethod
    def list_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def count(db: Session) -> int:
        return db.query(User).count()

    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        existing = UserService.get_by_email(db, user_in.email)
        if existing:
            raise ConflictException(f"User with email '{user_in.email}' already exists.")

        user = User(
            email=user_in.email.lower(),
            name=user_in.name,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role,
            is_active=user_in.is_active,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user_id: int, user_in: UserUpdate) -> User:
        user = UserService.get_by_id(db, user_id)
        if not user:
            raise NotFoundException("User", user_id)

        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        if "email" in update_data and update_data["email"]:
            new_email = update_data["email"].lower()
            if new_email != user.email:
                if UserService.get_by_email(db, new_email):
                    raise ConflictException(f"User with email '{new_email}' already exists.")
                update_data["email"] = new_email

        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def deactivate(db: Session, user_id: int) -> User:
        user = UserService.get_by_id(db, user_id)
        if not user:
            raise NotFoundException("User", user_id)
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
