import joblib
import os
import threading
from typing import Any

class ModelRegistry:
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self._models = {}
        self._m1_lock = threading.Lock()

    def get_m1_scorer(self) -> Any:
        """Loads and returns the M1 transaction scorer model (VotingClassifier)."""
        if "m1_scorer" not in self._models:
            with self._m1_lock:
                # Double-check pattern
                if "m1_scorer" not in self._models:
                    model_path = os.path.join("models", "m1_scorer.pkl")
                    if not os.path.exists(model_path):
                        # Fallback to app/models if top-level models not found (just in case)
                        alt_path = os.path.join("app", "models", "m1_scorer.pkl")
                        if os.path.exists(alt_path):
                            model_path = alt_path
                        else:
                            raise RuntimeError("M1 model not found — run ml_training/train_m1_scorer.py first")
                    
                    print(f"Loading M1 model from {model_path}...")
                    try:
                        self._models["m1_scorer"] = joblib.load(model_path)
                    except Exception as e:
                        raise RuntimeError(f"Failed to load M1 model: {str(e)}")
        
        return self._models["m1_scorer"]

# Singleton instance
registry = ModelRegistry()
