import os
import json
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.ml.model_registry import registry

router = APIRouter()

CTC_WINDOW_SECONDS = 300  # 5-minute CTC window

class CallRequest(BaseModel):
    transcript: str
    caller_number: Optional[str] = None  # Unknown caller number, if available
    payer_upi_id: Optional[str] = None   # Logged-in user's UPI ID for CTC tracking

class TruecallerRequest(BaseModel):
    phone_number: str

@router.post("/analyze")
async def analyze_call(request: CallRequest):
    """
    M4: Voice Intent Analysis
    1. Classifies call transcript for urgency/fraud intents (URGENCY, IMPERSONATION, etc.)
    2. If fraud detected and caller is unknown, stores CTC timestamp in Redis
    3. Also checks Truecaller-style spam reputation for caller number
    """
    try:
        # ── M4 Intent Classification ─────────────────────────────────────
        analyzer = registry.get_m4_classifier()
        result = analyzer.classify_transcript(request.transcript)

        # ── CTC: Store call event if fraud signals detected ───────────────
        # Check if 2+ patterns are detected (multi-intent fraud)
        detected_patterns = result.get("detected_patterns", [])
        fraud_intents_detected = len(detected_patterns) >= 2 or result.get("risk_level") == "HIGH"

        import logging
        logging.getLogger(__name__).info(f"CTC DEBUG: payer_id={request.payer_upi_id}, fraud_detected={fraud_intents_detected}, patterns={detected_patterns}")

        # ── Truecaller simulation ─────────────────────────────────────────
        truecaller_result = None
        if request.caller_number:
            truecaller_result = _check_truecaller(request.caller_number)

        # Store CTC event in Redis if unknown caller + fraud intents
        ctc_stored = False
        if request.payer_upi_id and fraud_intents_detected:
            ctc_stored = await _store_ctc_event(request.payer_upi_id)

        return {
            **result,
            "truecaller": truecaller_result,
            "ctc_window_started": ctc_stored,
            "ctc_window_seconds": CTC_WINDOW_SECONDS,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/truecaller/check")
async def truecaller_check(request: TruecallerRequest):
    """
    Truecaller-style spam reputation check for a phone number.
    Simulated — in production this calls the Truecaller Business API.
    """
    result = _check_truecaller(request.phone_number)
    return result


def _check_truecaller(phone_number: str) -> dict:
    """
    Simulated Truecaller Business API integration.
    In production: POST to https://api4.truecaller.com/v1/lookup with API key.
    Returns spam probability, labels, and community report count.
    """
    phone_clean = phone_number.strip().replace(" ", "").replace("-", "")
    
    # Known spam number patterns (simulation)
    is_known_spam = any([
        phone_clean.startswith("1800"),         # fake toll-free
        phone_clean.startswith("140"),           # telemarketing ISD range
        len(phone_clean) not in [10, 12, 13],   # invalid length
        phone_clean.endswith("0000"),            # suspicious round patterns
        phone_clean.endswith("9999"),
    ])

    report_count = 0
    spam_score = 0.0
    labels = []

    if is_known_spam:
        spam_score = 0.85 + (hash(phone_clean) % 15) / 100.0
        report_count = 50 + (hash(phone_clean) % 200)
        labels = ["Suspected Fraud", "Financial Scam"]
    else:
        spam_score = max(0.0, (hash(phone_clean) % 20) / 100.0)
        report_count = hash(phone_clean) % 5

    return {
        "phone_number": phone_number,
        "spam_score": round(min(1.0, spam_score), 3),
        "is_spam": is_known_spam or spam_score > 0.5,
        "labels": labels,
        "community_reports": report_count,
        "source": "Truecaller (simulated)",
        "note": "Live integration requires Truecaller Business API key"
    }


async def _store_ctc_event(payer_upi_id: str) -> bool:
    """Store call timestamp in Redis to activate the 5-minute CTC window."""
    try:
        import redis.asyncio as redis_async
        REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = redis_async.from_url(REDIS_URL, decode_responses=True)
        key = f"ctc:last_unknown_call:{payer_upi_id}"
        now_iso = datetime.now(timezone.utc).isoformat()
        await r.setex(key, CTC_WINDOW_SECONDS + 60, now_iso)  # slight buffer
        await r.close()
        return True
    except Exception as e:
        import traceback
        import logging
        logging.getLogger(__name__).error(f"CTC Store Error: {e}\n{traceback.format_exc()}")
        return False
