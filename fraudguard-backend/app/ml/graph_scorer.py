"""
M6 Graph Risk Scorer
Computes graph_risk_score for a UPI ID using the trained M6 GraphSAGE model.
Scores are cached in Redis for 24 hours (matching nightly retrain cycle).
"""
import numpy as np
import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

REDIS_TTL = 24 * 3600  # 24 hours


def _build_graph_features(upi_id: str, redis_client=None) -> np.ndarray:
    """
    Build graph-level feature vector for a UPI ID.
    In production this would query a graph DB/transaction table.
    We use Redis-cached stats when available, else fallback heuristics.
    """
    stats = {}
    if redis_client:
        try:
            raw = redis_client.get(f"graph:stats:{upi_id}")
            if raw:
                stats = json.loads(raw)
        except Exception:
            pass

    own_fraud_rate         = float(stats.get("own_fraud_rate", 0.0))
    neighbor_fraud_rate    = float(stats.get("neighbor_fraud_rate", 0.0))
    in_degree              = float(stats.get("in_degree", 5))
    out_degree             = float(stats.get("out_degree", 5))
    clustering_coeff       = float(stats.get("clustering_coefficient", 0.1))
    betweenness            = float(stats.get("betweenness_centrality", 0.05))
    avg_neighbor_age       = float(stats.get("avg_neighbor_account_age", 365))
    page_rank              = float(stats.get("page_rank_score", 0.1))
    two_hop_fraud_rate     = float(stats.get("two_hop_fraud_rate", 0.0))
    community_density      = float(stats.get("community_fraud_density", 0.0))

    # Heuristic boosts for obviously bad IDs (keyword signals)
    upi_lower = upi_id.lower()
    if any(k in upi_lower for k in ["fraud", "fake", "scam", "hack"]):
        own_fraud_rate     = max(own_fraud_rate, 0.7)
        neighbor_fraud_rate = max(neighbor_fraud_rate, 0.4)
        community_density  = max(community_density, 0.5)

    return np.array([[
        own_fraud_rate, neighbor_fraud_rate, in_degree, out_degree,
        clustering_coeff, betweenness, avg_neighbor_age, page_rank,
        two_hop_fraud_rate, community_density
    ]], dtype=np.float32)


def get_graph_risk_score(upi_id: str, redis_client=None) -> float:
    """
    Returns graph_risk_score in [0.0, 1.0] for a UPI ID.
    Checks Redis cache first, then runs M6 model.
    """
    cache_key = f"graph:risk:{upi_id}"

    # Check cache
    if redis_client:
        try:
            cached = redis_client.get(cache_key)
            if cached is not None:
                return float(cached)
        except Exception:
            pass

    # Run M6 model
    score = 0.1  # safe default
    try:
        from app.ml.model_registry import registry
        m6 = registry.get_m6_graph()
        features = _build_graph_features(upi_id, redis_client)
        prob_fraud = float(m6.predict_proba(features)[0][1])
        score = prob_fraud
    except Exception as e:
        logger.warning(f"M6 graph scoring failed for {upi_id}: {e}")

    # Cache result
    if redis_client:
        try:
            redis_client.setex(cache_key, REDIS_TTL, str(score))
        except Exception:
            pass

    return score
