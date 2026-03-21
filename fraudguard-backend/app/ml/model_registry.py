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
        self._m3_lock = threading.Lock()

    def get_m1_scorer(self) -> Any:
        # ... (rest of get_m1_scorer remains the same) ...
        if "m1_scorer" not in self._models:
            with self._m1_lock:
                if "m1_scorer" not in self._models:
                    model_path = os.path.join("models", "m1_scorer.pkl")
                    if not os.path.exists(model_path):
                        alt_path = os.path.join("app", "models", "m1_scorer.pkl")
                        if os.path.exists(alt_path):
                            model_path = alt_path
                        else:
                            raise RuntimeError("M1 model not found — run ml_training/train_m1_scorer.py first")
                    
                    self._models["m1_scorer"] = joblib.load(model_path)
        return self._models["m1_scorer"]

    def get_m3_classifier(self) -> Any:
        """Loads and returns the M3 SMS classifier model (SMSClassifier)."""
        if "m3_sms" not in self._models:
            with self._m3_lock:
                if "m3_sms" not in self._models:
                    from app.ml.sms_classifier import SMSClassifier
                    self._models["m3_sms"] = SMSClassifier()
        return self._models["m3_sms"]

# Singleton instance
registry = ModelRegistry()
