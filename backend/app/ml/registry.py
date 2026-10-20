"""ML Model registry for versioned artifact persistence and metadata management."""

import os
import json
import joblib
from typing import Dict, Any, Optional, Tuple
import datetime


class ModelRegistry:
    ARTIFACT_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "ml_artifacts")
    )

    @classmethod
    def get_artifact_dir(cls) -> str:
        os.makedirs(cls.ARTIFACT_DIR, exist_ok=True)
        return cls.ARTIFACT_DIR

    @classmethod
    def save_artifact(
        cls,
        run_id: str,
        model: Any,
        feature_names: list,
        metadata: Dict[str, Any],
    ) -> Dict[str, str]:
        """Save fitted model object and metadata JSON."""
        dir_path = cls.get_artifact_dir()
        model_filename = f"model_{run_id}.joblib"
        meta_filename = f"metadata_{run_id}.json"

        model_path = os.path.join(dir_path, model_filename)
        meta_path = os.path.join(dir_path, meta_filename)

        # Save model
        joblib.dump(model, model_path)

        # Save metadata
        metadata["run_id"] = run_id
        metadata["saved_at"] = datetime.datetime.utcnow().isoformat()
        metadata["model_file"] = model_filename
        metadata["feature_names"] = feature_names

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return {
            "model_path": model_path,
            "metadata_path": meta_path,
        }

    @classmethod
    def load_artifact(cls, run_id: str) -> Tuple[Any, Dict[str, Any]]:
        dir_path = cls.get_artifact_dir()
        model_path = os.path.join(dir_path, f"model_{run_id}.joblib")
        meta_path = os.path.join(dir_path, f"metadata_{run_id}.json")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model artifact not found: {model_path}")

        model = joblib.load(model_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        return model, meta

    @classmethod
    def list_artifacts(cls) -> list:
        dir_path = cls.get_artifact_dir()
        runs = []
        for f in os.listdir(dir_path):
            if f.startswith("metadata_") and f.endswith(".json"):
                with open(os.path.join(dir_path, f), "r", encoding="utf-8") as meta_f:
                    runs.append(json.load(meta_f))
        return sorted(runs, key=lambda x: x.get("saved_at", ""), reverse=True)
