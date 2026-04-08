"""
M6: Fraud Network Graph Model (GraphSAGE)
Models UPI ecosystem as a directed graph (nodes=UPIIDs, edges=transactions).
Runs as a nightly Celery task, produces graph_risk_score cached in Redis.
Simulates GraphSAGE using GBDT on aggregated neighbor features (no PyG dependency).
"""
import numpy as np
import json
import joblib
import os
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

np.random.seed(42)

# ─── Synthetic graph-level feature generation ────────────────────────────────
# Features per node (UPI ID):
#   0  own_fraud_rate          — fraction of own txs marked fraud
#   1  neighbor_fraud_rate     — avg fraud rate of direct neighbors (1-hop)
#   2  in_degree               — number of unique payers
#   3  out_degree              — number of unique payees
#   4  clustering_coefficient  — how interconnected the neighbors are
#   5  betweenness_centrality  — how often this node is on shortest paths
#   6  avg_neighbor_account_age
#   7  page_rank_score
#   8  two_hop_fraud_rate      — avg fraud rate of 2-hop neighbors
#   9  community_fraud_density — fraction of same-community nodes flagged

def gen_node(is_fraud: bool) -> list:
    if is_fraud:
        own_fraud_rate          = np.random.uniform(0.3, 1.0)
        neighbor_fraud_rate     = np.random.uniform(0.2, 0.8)
        in_degree               = np.random.randint(1, 20)
        out_degree              = np.random.randint(1, 10)
        clustering_coefficient  = np.random.uniform(0.5, 1.0)
        betweenness             = np.random.uniform(0.3, 1.0)
        avg_neighbor_age        = np.random.uniform(0, 60)
        page_rank               = np.random.uniform(0.5, 1.0)
        two_hop_fraud_rate      = np.random.uniform(0.2, 0.7)
        community_density       = np.random.uniform(0.3, 1.0)
    else:
        own_fraud_rate          = np.random.uniform(0.0, 0.02)
        neighbor_fraud_rate     = np.random.uniform(0.0, 0.05)
        in_degree               = np.random.randint(5, 500)
        out_degree              = np.random.randint(2, 200)
        clustering_coefficient  = np.random.uniform(0.0, 0.3)
        betweenness             = np.random.uniform(0.0, 0.2)
        avg_neighbor_age        = np.random.uniform(180, 2000)
        page_rank               = np.random.uniform(0.0, 0.3)
        two_hop_fraud_rate      = np.random.uniform(0.0, 0.03)
        community_density       = np.random.uniform(0.0, 0.05)

    return [
        own_fraud_rate, neighbor_fraud_rate, float(in_degree), float(out_degree),
        clustering_coefficient, betweenness, avg_neighbor_age, page_rank,
        two_hop_fraud_rate, community_density
    ]

N_LEGIT, N_FRAUD = 10000, 1500
print(f"Generating {N_LEGIT} legit + {N_FRAUD} fraud graph nodes...")

X_legit = [gen_node(False) for _ in range(N_LEGIT)]
X_fraud = [gen_node(True)  for _ in range(N_FRAUD)]
X = np.array(X_legit + X_fraud, dtype=np.float32)
y = np.array([0]*N_LEGIT + [1]*N_FRAUD)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set: {len(X_train)} | Test set: {len(X_test)}")

model = GradientBoostingClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=5,
    subsample=0.8,
    random_state=42
)

print("Training M6 GraphSAGE-equivalent model...")
model.fit(X_train, y_train)

y_proba = model.predict_proba(X_test)[:, 1]
y_pred  = (y_proba >= 0.5).astype(int)

roc = roc_auc_score(y_test, y_proba)
p   = precision_score(y_test, y_pred)
r   = recall_score(y_test, y_pred)
f1  = f1_score(y_test, y_pred)

print(f"\nM6 Metrics:")
print(f"  ROC-AUC:   {roc:.4f}")
print(f"  Precision: {p:.4f}")
print(f"  Recall:    {r:.4f}")
print(f"  F1:        {f1:.4f}")

model_path   = os.path.join(MODELS_DIR, "m6_graph_sage.pkl")
metrics_path = os.path.join(MODELS_DIR, "m6_metrics.json")

joblib.dump(model, model_path)
print(f"\nModel saved → {model_path}")

FEATURE_NAMES = [
    "own_fraud_rate", "neighbor_fraud_rate", "in_degree", "out_degree",
    "clustering_coefficient", "betweenness_centrality", "avg_neighbor_account_age",
    "page_rank_score", "two_hop_fraud_rate", "community_fraud_density"
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
print("\nM6 training complete!")
