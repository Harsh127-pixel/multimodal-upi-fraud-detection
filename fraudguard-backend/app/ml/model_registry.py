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
        self._m2_lock = threading.Lock()
        self._m3_lock = threading.Lock()
        self._m4_lock = threading.Lock()
        self._m6_lock = threading.Lock()

    def get_m1_scorer(self) -> Any:
        # returns M1 VotingClassifier...
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

    def get_m2_reputation(self) -> Any:
        """Loads and returns M2 LightGBM UPI Identity Reputation model."""
        if "m2_reputation" not in self._models:
            with self._m2_lock:
                if "m2_reputation" not in self._models:
                    model_path = os.path.join("models", "m2_upi_reputation.pkl")
                    if not os.path.exists(model_path):
                        alt_path = os.path.join("app", "models", "m2_upi_reputation.pkl")
                        if os.path.exists(alt_path):
                            model_path = alt_path
                        else:
                            raise RuntimeError("M2 model not found — run ml_training/train_m2_upi_reputation.py first")
                    self._models["m2_reputation"] = joblib.load(model_path)
        return self._models["m2_reputation"]

    def get_m3_classifier(self) -> Any:
        """Loads and returns the M3 SMS classifier model (SMSClassifier)."""
        if "m3_sms" not in self._models:
            with self._m3_lock:
                if "m3_sms" not in self._models:
                    from app.ml.sms_classifier import SMSClassifier
                    self._models["m3_sms"] = SMSClassifier()
        return self._models["m3_sms"]

    def get_m4_classifier(self) -> Any:
        """Loads and returns the M4 Call intent classifier (CallIntentClassifier)."""
        if "m4_call" not in self._models:
            with self._m4_lock:
                if "m4_call" not in self._models:
                    from app.ml.call_intent import CallIntentClassifier
                    self._models["m4_call"] = CallIntentClassifier()
        return self._models["m4_call"]

    def get_m6_graph(self) -> Any:
        """Loads M6 GraphSAGE-equivalent fraud network model."""
        if "m6_graph" not in self._models:
            with self._m6_lock:
                if "m6_graph" not in self._models:
                    model_path = os.path.join("models", "m6_graph_sage.pkl")
                    if not os.path.exists(model_path):
                        alt_path = os.path.join("app", "models", "m6_graph_sage.pkl")
                        if os.path.exists(alt_path):
                            model_path = alt_path
                        else:
                            raise RuntimeError("M6 model not found — run ml_training/train_m6_graph.py first")
                    self._models["m6_graph"] = joblib.load(model_path)
        return self._models["m6_graph"]

    def invalidate_m6(self):
        """Clear cached M6 model so next call reloads from disk (after nightly retrain)."""
        with self._m6_lock:
            self._models.pop("m6_graph", None)

# Singleton instance
registry = ModelRegistry()
