"""Bootstrap database for cloud deployments (Render, Railway, Fly.io, etc.).
Ensures tables exist, admin is seeded, and initial dataset is imported if empty.
"""

import os
import sys

# Ensure repository root is on path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app.db.base import Base
from backend.app.db.session import engine, SessionLocal
import backend.app.db.models  # Register all models
from backend.app.db.models.medicine import Medicine
from backend.app.main import seed_admin_if_needed
from backend.app.services.dataset_service import DatasetService
from backend.app.services.risk_service import RiskService


def bootstrap():
    print("[bootstrap] 1/4 Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    print("[bootstrap] 2/4 Verifying admin user...")
    seed_admin_if_needed()

    db = SessionLocal()
    try:
        med_count = db.query(Medicine).count()
        print(f"[bootstrap] Found {med_count} existing medicines.")

        if med_count == 0:
            print("[bootstrap] 3/4 Importing 155,210 rows and 85 medicines from dataset pack...")
            res = DatasetService.run_import(db)
            print(f"[bootstrap] Import complete: {res.daily_records_count} records imported.")

            print("[bootstrap] 4/4 Running initial stock-out risk engine...")
            risk_res = RiskService.run_all(db)
            eval_count = risk_res.get("medicines_evaluated", 0) if isinstance(risk_res, dict) else getattr(risk_res, "medicines_evaluated", 0)
            print(f"[bootstrap] Risk engine evaluated {eval_count} medicines.")
        else:
            print("[bootstrap] 3/4 Database is already populated. Skipping import.")
            print("[bootstrap] 4/4 Ready to serve traffic.")
    finally:
        db.close()

    print("[bootstrap] Database bootstrap completed successfully!")


if __name__ == "__main__":
    bootstrap()

