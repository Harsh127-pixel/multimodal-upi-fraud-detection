from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List
import numpy as np

from app.core.database import get_db
from app.models.upi_profile import UPIProfile
from app.ml.model_registry import registry

router = APIRouter()

class UPIVerifyRequest(BaseModel):
    upi_id: str

class UPIVerifyResponse(BaseModel):
    risk_score: int
    risk_level: str
    risk_signals: List[str]
    model: str  # which model was used

# Feature names for M2 (must match train_m2_upi_reputation.py)
# [account_age_days, total_tx_volume, unique_senders, fraud_report_rate,
#  name_handle_similarity, avg_tx_amount, tx_count_last_7d,
#  blacklist_community, npci_complaint_flag]

def _build_m2_features(upi_id: str, profile) -> np.ndarray:
    """Convert UPI profile (or lack of one) into M2's 9-feature vector."""
    if profile:
        account_age_days       = float(profile.account_age_days or 0)
        total_tx_volume        = float(profile.total_tx_volume or 0)
        unique_senders         = float(profile.unique_senders or 0)
        fraud_report_rate      = float(profile.fraud_count or 0) / max(1, float(profile.tx_count or 1))
        name_handle_similarity = float(profile.name_handle_similarity or 0.5)
        avg_tx_amount          = float(profile.avg_tx_amount or 0)
        tx_count_last_7d       = float(profile.tx_count_last_7d or 0)
        blacklist_community    = 1.0 if profile.blacklisted else 0.0
        npci_complaint_flag    = 1.0 if (profile.fraud_count or 0) > 0 else 0.0
    else:
        # Unknown UPI — use heuristic defaults leaning toward caution
        contains_fraud   = 1 if "fraud" in upi_id else 0
        contains_new     = 1 if "new" in upi_id else 0
        contains_scam    = 1 if any(k in upi_id for k in ["scam","fake","hack","cheat"]) else 0

        account_age_days       = 5.0 + (355.0 * (1 - contains_new))
        total_tx_volume        = 0.0 if contains_fraud else 50000.0
        unique_senders         = 1.0 if contains_new else 20.0
        fraud_report_rate      = 0.8 if contains_fraud else (0.5 if contains_scam else 0.0)
        name_handle_similarity = 0.2 if contains_fraud else (0.5 if contains_new else 0.8)
        avg_tx_amount          = 50000.0 if contains_fraud else 5000.0
        tx_count_last_7d       = 0.0 if contains_new else 15.0
        blacklist_community    = float(contains_fraud or contains_scam)
        npci_complaint_flag    = float(contains_fraud)

    return np.array([[
        account_age_days, total_tx_volume, unique_senders,
        fraud_report_rate, name_handle_similarity, avg_tx_amount,
        tx_count_last_7d, blacklist_community, npci_complaint_flag,
    ]], dtype=np.float32)


@router.post("/verify", response_model=UPIVerifyResponse)
async def verify_upi(request: UPIVerifyRequest, db: AsyncSession = Depends(get_db)):
    upi_id = request.upi_id.strip().lower()

    # 1. Fetch profile from DB (if exists)
    stmt = select(UPIProfile).where(UPIProfile.upi_id == upi_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    risk_signals: List[str] = []
    model_used = "rule-based"

    # 2. Try M2 LightGBM scoring
    try:
        m2 = registry.get_m2_reputation()
        features = _build_m2_features(upi_id, profile)
        prob_fraud = float(m2.predict_proba(features)[0][1])
        risk_score = int(prob_fraud * 100)
        model_used = "M2 LightGBM"
    except Exception:
        # Fall back to simple heuristics if M2 unavailable
        risk_score = 30
        if profile and profile.blacklisted:
            risk_score = 100
        elif profile and (profile.fraud_count or 0) >= 1:
            risk_score = min(100, 70 + (profile.fraud_count * 10))

    # 3. Hard overrides from DB
    if profile:
        if profile.blacklisted:
            risk_score = 100
            risk_signals.append("CRITICAL: This UPI ID is officially blacklisted by NPCI")
        if (profile.fraud_count or 0) >= 1:
            risk_signals.append(f"Warning: {profile.fraud_count} community fraud reports on this ID")
        if (profile.account_age_days or 365) < 30:
            risk_signals.append("Account registered less than 30 days ago")
    else:
        # signals for unknown IDs
        if "fraud" in upi_id or "fake" in upi_id or "scam" in upi_id:
            risk_signals.append("High-risk keywords detected in UPI ID")
        if "new" in upi_id:
            risk_signals.append("Newly registered UPI ID pattern detected")
        if risk_score < 40:
            risk_signals.append("No prior transaction history found — use caution")

    # 4. Risk level
    risk_score = min(100, max(0, risk_score))
    if risk_score < 40:
        level = "low"
        if not risk_signals:
            risk_signals.append("No significant risk factors identified")
    elif risk_score < 75:
        level = "medium"
        if not risk_signals:
            risk_signals.append("Moderate risk detected — verify before transacting")
    else:
        level = "high"
        if not risk_signals:
            risk_signals.append("High fraud probability detected by ML model")

    return {
        "risk_score": risk_score,
        "risk_level": level,
        "risk_signals": risk_signals[:5],
        "model": model_used,
    }
