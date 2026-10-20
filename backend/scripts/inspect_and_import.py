import os
import sys

# Ensure repository root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.db.base import Base
from backend.app.db.session import engine, SessionLocal
import backend.app.db.models  # load all models
from backend.app.services.dataset_service import DatasetService

def main():
    print("Verifying/creating all tables via SQLAlchemy...")
    Base.metadata.create_all(bind=engine)
    print("Tables verified.")

    db = SessionLocal()
    try:
        print("Starting dataset import into database...")
        res = DatasetService.run_import(db)
        print("Import result:", res.to_dict())
    finally:
        db.close()

if __name__ == "__main__":
    main()
