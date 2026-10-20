import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///./test_pharmastock.db"

from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.db.models.user import User, UserRole
from backend.app.core.security import get_password_hash
from backend.app.main import app

# Create test sqlite database
test_engine = create_engine("sqlite:///./test_pharmastock.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    try:
        Base.metadata.drop_all(bind=test_engine)
    except Exception:
        pass
    test_engine.dispose()
    try:
        if os.path.exists("./test_pharmastock.db"):
            os.remove("./test_pharmastock.db")
    except Exception:
        pass


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session: Session) -> User:
    user = db_session.query(User).filter(User.email == "test_admin@pharma.local").first()
    if not user:
        user = User(
            email="test_admin@pharma.local",
            name="Admin Tester",
            hashed_password=get_password_hash("AdminPass123!"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def staff_user(db_session: Session) -> User:
    user = db_session.query(User).filter(User.email == "test_staff@pharma.local").first()
    if not user:
        user = User(
            email="test_staff@pharma.local",
            name="Staff Tester",
            hashed_password=get_password_hash("StaffPass123!"),
            role=UserRole.PHARMACY_STAFF,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user
