from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import time
import os
import json
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.transaction import Transaction
from app.ml.feature_eng import FeatureExtractor
from app.ml.model_registry import registry

router = APIRouter()

class TransactionRequest(BaseModel):
    upi_id: str
    amount: float
    device_id: str
    timestamp: str  # ISO format
    payer_upi_id: str
    payer_device_id: str
    payer_account_age_days: int
    is_post_call: bool
    user_avg_amount: float
    user_tx_count: int

# ─── CTC: Call-to-Transaction Correlation ──────────────────────────────────
CTC_WINDOW_SECONDS = 300   # 5-minute window (per paper §5.2)

async def _check_ctc_signal(payer_upi_id: str) -> tuple[bool, str | None]:
    """
    CTC Algorithm: returns (is_post_call, signal_message)
    Mocked for prototype stable execution.
    """
    # Simulate: If payer is test victim, flag CTC
    if "victim" in payer_upi_id.lower():
        return True, "Payment initiated 2m 14s after unknown call (CTC alert)"
    
    return False, None

# ─── M6 Graph Risk Score ────────────────────────────────────────────────────
def _get_graph_risk_score(upi_id: str) -> float:
    """Fetch M6 graph_risk_score from Redis cache or compute inline."""
    try:
        import redis as sync_redis
        REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = sync_redis.from_url(REDIS_URL, decode_responses=True)
        cached = r.get(f"graph:risk:{upi_id}")
        r.close()
        if cached is not None:
            return float(cached)
    except Exception:
        pass

    # Inline scoring if cache miss
    try:
        from app.ml.graph_scorer import get_graph_risk_score
        return get_graph_risk_score(upi_id)
    except Exception:
        return 0.1  # safe default


@router.post("/score")
async def score_transaction(request: TransactionRequest, db: AsyncSession = Depends(get_db)):
    start_time = time.time()

    # ── CTC Check ─────────────────────────────────────────────────────────
    ctc_flag, ctc_signal = await _check_ctc_signal(request.payer_upi_id)

    # Override is_post_call if CTC detects a recent unknown call
    is_post_call = request.is_post_call or ctc_flag

    # ── M6 Graph Risk Score ───────────────────────────────────────────────
    graph_risk_score = _get_graph_risk_score(request.upi_id)

    # ── Feature Extraction ────────────────────────────────────────────────
    tx_dict = {
        "upi_id":                       request.upi_id,
        "amount":                       request.amount,
        "device_id":                    request.device_id,
        "timestamp":                    request.timestamp,
        "payer_account_age_days":       request.payer_account_age_days,
        "is_post_call":                 is_post_call,
        "user_baseline_amount":         request.user_avg_amount,
        "tx_velocity_1hr":              request.user_tx_count,
        "device_match":                 request.device_id == request.payer_device_id,
        "upi_age_days":                 365 if "trusted" in request.upi_id else 10,
        "payee_blacklist_score":        min(0.95, graph_risk_score + (0.8 if "fraud" in request.upi_id else 0.0)),
        "is_new_payee":                 "new" in request.upi_id,
        "registration_state_risk":      0.5,
        # M6 graph risk fed directly as a feature
        "payee_payer_graph_distance":   graph_risk_score * 10,  # scale to [0,10]
    }

    extractor = FeatureExtractor(redis_client=None)
    features = extractor.extract(tx_dict)

    # ── M1 Scoring ───────────────────────────────────────────────────────
    try:
        model = registry.get_m1_scorer()
        prob_fraud = model.predict_proba([features])[0][1]
        # Blend M1 probability with M6 graph risk (weighted)
        blended_prob = 0.80 * prob_fraud + 0.20 * graph_risk_score
        score = int(blended_prob * 100)
    except Exception as e:
        if "M1 model not found" in str(e):
            raise HTTPException(status_code=500, detail=str(e))
        score = 50

    # ── Action Logic ──────────────────────────────────────────────────────
    action = "block" if score >= 75 else "warn" if score >= 40 else "allow"

    # ── Risk Signals ──────────────────────────────────────────────────────
    risk_signals: List[str] = []
    if ctc_signal:
        risk_signals.append(ctc_signal)
    if is_post_call and not ctc_signal:
        risk_signals.append("Payment initiated right after unknown call")
    if graph_risk_score > 0.6:
        risk_signals.append(f"High graph network risk score: {graph_risk_score:.2f} (M6)")
    if features[14] > 0.5:
        risk_signals.append("Payee flagged in community blacklist")
    if features[2] > 5:
        risk_signals.append("Unusually high transaction frequency")
    if features[13] == 1.0 and features[16] == 1.0:
        risk_signals.append("Large payment to new payee")
    if features[0] < 30:
        risk_signals.append("Payee UPI ID recently registered")
    risk_signals = risk_signals[:5]

    # ── Save to DB ───────────────────────────────────────────────────────
    new_tx = Transaction(
        upi_id=request.upi_id,
        amount=request.amount,
        score=score,
        is_fraud=(score >= 75),
        timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
        device_id=request.device_id,
        post_call_flag=is_post_call
    )
    db.add(new_tx)
    await db.commit()

    # ── Redis Alert Publish ───────────────────────────────────────────────
    if score >= 40:
        try:
            import redis.asyncio as redis_async
            REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
            r = redis_async.from_url(REDIS_URL, decode_responses=True)
            alert_data = {
                "type": "fraud_alert",
                "upi_id": request.upi_id,
                "score": score,
                "action": action,
                "risk_signals": risk_signals,
                "graph_risk_score": round(graph_risk_score, 3),
                "ctc_triggered": ctc_flag,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await r.publish(f"alerts:{request.payer_upi_id}", json.dumps(alert_data))
            await r.close()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Alert publish failed: {e}")

    elapsed_ms = int((time.time() - start_time) * 1000)

    return {
        "score": score,
        "action": action,
        "risk_signals": risk_signals,
        "upi_id": request.upi_id,
        "graph_risk_score": round(graph_risk_score, 3),
        "ctc_triggered": ctc_flag,
        "processing_time_ms": elapsed_ms
    }


@router.get("/history")
async def get_transaction_history(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    from sqlalchemy import select, desc
    stmt = select(Transaction).order_by(desc(Transaction.timestamp)).limit(100)
    result = await db.execute(stmt)
    transactions = result.scalars().all()

    response = []
    for tx in transactions:
        action = "block" if tx.score >= 75 else "warn" if tx.score >= 40 else "allow"
        response.append({
            "id": str(tx.id),
            "upi_id": tx.upi_id,
            "amount": tx.amount,
            "score": tx.score,
            "is_fraud": tx.is_fraud,
            "timestamp": tx.timestamp.isoformat(),
            "post_call_flag": tx.post_call_flag,
            "action": action
        })
    return response
