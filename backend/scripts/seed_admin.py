#!/usr/bin/env python3
"""
Seed script to create the initial Administrator and default role accounts
from environment configuration.
"""
import sys
import os

# Add parent directory to sys.path so backend package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.core.config import settings
from backend.app.db.base import Base
from backend.app.db.session import engine, SessionLocal
from backend.app.db.models.user import User, UserRole
from backend.app.core.security import get_password_hash


def seed_users():
    print("Connecting to database:", settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    default_accounts = [
        {
            "email": settings.FIRST_SUPERUSER_EMAIL.lower(),
            "name": settings.FIRST_SUPERUSER_NAME,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
            "role": UserRole.ADMIN,
        },
        {
            "email": "manager@pharmastock.local",
            "name": "Rajesh Sharma",
            "password": "ManagerPassword123!",
            "role": UserRole.INVENTORY_MANAGER,
        },
        {
            "email": "staff@pharmastock.local",
            "name": "Ananya Patel",
            "password": "StaffPassword123!",
            "role": UserRole.PHARMACY_STAFF,
        },
    ]

    try:
        for acc in default_accounts:
            existing = db.query(User).filter(User.email == acc["email"]).first()
            if existing:
                print(f"[EXISTS] User '{acc['email']}' ({existing.role.value}) already exists.")
            else:
                user = User(
                    email=acc["email"],
                    name=acc["name"],
                    hashed_password=get_password_hash(acc["password"]),
                    role=acc["role"],
                    is_active=True,
                )
                db.add(user)
                db.commit()
                print(f"[CREATED] Seeded user '{acc['email']}' as {acc['role'].value}.")
        print("\nAll default user accounts successfully provisioned.")
    except Exception as e:
        print("Error during seed:", e)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
