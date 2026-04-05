"""
conftest.py — runs before any test collection, so module-level mocks land
before the heavy ML packages (numpy, torch, etc.) are imported via main.py.
"""
import sys
from unittest.mock import MagicMock

_ML_STUBS = [
    "numpy",
    "pandas",
    "sklearn",
    "sklearn.ensemble",
    "sklearn.preprocessing",
    "sklearn.pipeline",
    "xgboost",
    "torch",
    "torch.nn",
    "transformers",
    "librosa",
    "whisper",
    "joblib",
    "scipy",
    "scipy.sparse",
    "imbalanced_learn",
    "soundfile",
]

for _mod in _ML_STUBS:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()
