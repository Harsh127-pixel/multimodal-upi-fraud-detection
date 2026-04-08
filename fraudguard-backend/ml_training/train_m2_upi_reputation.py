"""
M2: UPI Identity Reputation Model
Uses LightGBM on account metadata to score individual UPI IDs.
Features: account age, tx volume, unique senders, fraud report rate, name-handle match
"""
import numpy as np
import json
import joblib
import os
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

try:
    import lightgbm as lgb
except ImportError:
    print("Installing lightgbm...")
    os.system("pip install lightgbm")
    import lightgbm as lgb

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

np.random.seed(42)
N_LEGIT = 8000
N_FRAUD = 1000
N = N_LEGIT + N_FRAUD

def generate_samples(n, is_fraud: bool):
    """Generate synthetic UPI ID profile features."""
    rows = []
    for _ in range(n):
        if is_fraud:
            account_age_days        = np.random.randint(0, 30)          # newly created
            total_tx_volume         = np.random.uniform(0, 50000)
            unique_senders          = np.random.randint(1, 5)
            fraud_report_rate       = np.random.uniform(0.1, 1.0)       # high reports
            name_handle_similarity  = np.random.uniform(0.0, 0.4)       # mismatch
            avg_tx_amount           = np.random.uniform(5000, 100000)   # large
            tx_count_last_7d        = np.random.randint(0, 10)
            blacklist_community     = np.random.choice([0, 1], p=[0.2, 0.8])
            npci_complaint_flag     = np.random.choice([0, 1], p=[0.3, 0.7])
        else:
            account_age_days        = np.random.randint(90, 3000)       # established
            total_tx_volume         = np.random.uniform(10000, 2000000)
            unique_senders          = np.random.randint(5, 200)
            fraud_report_rate       = np.random.uniform(0.0, 0.02)      # near-zero
            name_handle_similarity  = np.random.uniform(0.7, 1.0)       # matches
            avg_tx_amount           = np.random.uniform(500, 15000)
            tx_count_last_7d        = np.random.randint(3, 100)
            blacklist_community     = 0
            npci_complaint_flag     = 0

        rows.append([
            account_age_days,
            total_tx_volume,
            unique_senders,
            fraud_report_rate,
            name_handle_similarity,
            avg_tx_amount,
            tx_count_last_7d,
            blacklist_community,
            npci_complaint_flag,
        ])
    return np.array(rows, dtype=np.float32)

print("Generating training data...")
X_fraud  = generate_samples(N_FRAUD, is_fraud=True)
X_legit  = generate_samples(N_LEGIT, is_fraud=False)
X        = np.vstack([X_legit, X_fraud])
y        = np.array([0]*N_LEGIT + [1]*N_FRAUD)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Training set: {len(X_train)} | Test set: {len(X_test)}")

params = {
    "objective":       "binary",
    "metric":          "auc",
    "boosting_type":   "gbdt",
    "num_leaves":      31,
    "learning_rate":   0.05,
    "n_estimators":    300,
    "scale_pos_weight": N_LEGIT / N_FRAUD,
    "random_state":    42,
    "verbose":         -1,
}

model = lgb.LGBMClassifier(**params)
print("Training M2 LightGBM UPI Reputation model...")
model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
)

y_proba = model.predict_proba(X_test)[:, 1]
y_pred  = (y_proba >= 0.5).astype(int)

roc  = roc_auc_score(y_test, y_proba)
p    = precision_score(y_test, y_pred)
r    = recall_score(y_test, y_pred)
f1   = f1_score(y_test, y_pred)

print(f"\nM2 Metrics:")
print(f"  ROC-AUC:   {roc:.4f}")
print(f"  Precision: {p:.4f}")
print(f"  Recall:    {r:.4f}")
print(f"  F1:        {f1:.4f}")

model_path   = os.path.join(MODELS_DIR, "m2_upi_reputation.pkl")
metrics_path = os.path.join(MODELS_DIR, "m2_metrics.json")

joblib.dump(model, model_path)
print(f"\nModel saved → {model_path}")

FEATURE_NAMES = [
    "account_age_days", "total_tx_volume", "unique_senders",
    "fraud_report_rate", "name_handle_similarity", "avg_tx_amount",
    "tx_count_last_7d", "blacklist_community", "npci_complaint_flag"
]
importance = dict(zip(FEATURE_NAMES, model.feature_importances_.tolist()))

metrics = {
    "roc_auc": round(roc, 4),
    "precision": round(p, 4),
    "recall": round(r, 4),
    "f1_score": round(f1, 4),
    "feature_importance": importance
}
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"Metrics saved → {metrics_path}")
print("\nM2 training complete!")
