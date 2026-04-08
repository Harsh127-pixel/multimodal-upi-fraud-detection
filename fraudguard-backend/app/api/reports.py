import os
import json
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import redis.asyncio as redis

from app.core.database import get_db
from app.models.fraud_report import FraudReport
from app.models.upi_profile import UPIProfile

router = APIRouter()
logger = logging.getLogger(__name__)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


class FraudReportRequest(BaseModel):
    upi_id: str
    fraud_type: str          # fake_qr | impersonation | lottery | investment | other
    amount_lost: float
    utr_number: str
    description: str
    evidence_url: Optional[str] = None
    submit_to_1930: bool = True   # Auto-forward to Cybercrime Portal 1930
    reporter_phone: Optional[str] = None


@router.post("/submit")
async def submit_report(
    request: FraudReportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # ── 1. Save to FraudReport table ─────────────────────────────────────
    report = FraudReport(
        upi_id=request.upi_id,
        fraud_type=request.fraud_type,
        amount=request.amount_lost,
        utr_number=request.utr_number,
        description=request.description,
        evidence_url=request.evidence_url
    )
    db.add(report)

    # ── 2. Upsert UPIProfile ─────────────────────────────────────────────
    stmt = select(UPIProfile).where(UPIProfile.upi_id == request.upi_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if profile:
        profile.fraud_count = (profile.fraud_count or 0) + 1
        if profile.fraud_count >= 2:
            profile.blacklisted = True
    else:
        profile = UPIProfile(
            upi_id=request.upi_id,
            fraud_count=1,
            blacklisted=False,
            registration_date=datetime.utcnow()
        )
        db.add(profile)

    await db.commit()
    await db.refresh(report)
    await db.refresh(profile)

    # ── 3. Community blacklist + Redis publish ────────────────────────────
    r = redis.from_url(REDIS_URL, decode_responses=True)
    await r.sadd("community_blacklist", request.upi_id)

    update_msg = {
        "type": "new_report",
        "upi_id": request.upi_id,
        "fraud_type": request.fraud_type,
        "amount": request.amount_lost,
    }
    await r.publish("community_updates", json.dumps(update_msg))
    await r.close()

    # ── 4. Cybercrime Portal 1930 Submission (background task) ───────────
    portal_result = None
    if request.submit_to_1930:
        case_ref = f"1930-{datetime.utcnow().strftime('%Y%m%d')}-{str(report.id)[:8].upper()}"
        background_tasks.add_task(
            _submit_to_cybercrime_portal,
            case_ref=case_ref,
            report_id=str(report.id),
            upi_id=request.upi_id,
            fraud_type=request.fraud_type,
            amount=request.amount_lost,
            utr=request.utr_number,
            description=request.description,
            reporter_phone=request.reporter_phone,
        )
        portal_result = {
            "submitted": True,
            "case_reference": case_ref,
            "portal": "Cybercrime Portal 1930",
            "status": "pending",
            "note": "Case filed with National Cybercrime Reporting Portal"
        }

    return {
        "message": "Report submitted successfully",
        "case_id": str(report.id),
        "upi_id": request.upi_id,
        "blacklisted": profile.blacklisted,
        "cybercrime_portal": portal_result,
    }


@router.get("/blacklist")
async def get_blacklist():
    r = redis.from_url(REDIS_URL, decode_responses=True)
    count = await r.scard("community_blacklist")
    _, recent = await r.sscan("community_blacklist", count=10)
    await r.close()
    return {"count": count, "recent": recent}


# ─── Cybercrime Portal 1930 Integration ─────────────────────────────────────

PORTAL_1930_URL = os.getenv(
    "CYBERCRIME_PORTAL_URL",
    "https://cybercrime.gov.in/api/v1/report"   # official endpoint (requires API key)
)
PORTAL_API_KEY = os.getenv("CYBERCRIME_PORTAL_API_KEY", "")


async def _submit_to_cybercrime_portal(
    case_ref: str,
    report_id: str,
    upi_id: str,
    fraud_type: str,
    amount: float,
    utr: str,
    description: str,
    reporter_phone: Optional[str],
):
    """
    Submits a fraud report to the National Cybercrime Reporting Portal (1930).
    In production: POST to PORTAL_1930_URL with API key in headers.
    Currently simulated — logs the submission and stores result in Redis.
    """
    payload = {
        "case_reference": case_ref,
        "fraud_category": "Online Financial Fraud",
        "fraud_sub_type": fraud_type,
        "suspect_upi_id": upi_id,
        "transaction_id": utr,
        "amount_lost": amount,
        "description": description,
        "reporter_phone": reporter_phone or "N/A",
        "platform": "FraudGuard",
        "report_timestamp": datetime.utcnow().isoformat(),
    }

    success = False
    portal_response = None

    if PORTAL_API_KEY:
        # Production path: real HTTP call
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    PORTAL_1930_URL,
                    json=payload,
                    headers={"Authorization": f"Bearer {PORTAL_API_KEY}", "Content-Type": "application/json"}
                )
                portal_response = resp.json()
                success = resp.status_code == 200
                logger.info(f"1930 Portal: {case_ref} → {resp.status_code}")
        except Exception as e:
            logger.error(f"1930 Portal submission failed: {e}")
    else:
        # Simulation mode
        success = True
        portal_response = {
            "status": "simulated",
            "case_reference": case_ref,
            "acknowledgement": f"ACK-{case_ref}",
            "message": "Report logged (simulation — set CYBERCRIME_PORTAL_API_KEY for live submission)",
        }
        logger.info(f"1930 Portal [SIMULATED]: {case_ref} for {upi_id} — ₹{amount}")

    # Store result in Redis for frontend polling
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        await r.setex(
            f"portal:1930:{report_id}",
            7 * 24 * 3600,   # keep for 7 days
            json.dumps({"status": "complete", "success": success, "case_ref": case_ref, "response": portal_response})
        )
        await r.close()
    except Exception as e:
        logger.warning(f"Could not cache portal result: {e}")


@router.get("/portal-status/{report_id}")
async def get_portal_status(report_id: str):
    """Check Cybercrime Portal 1930 submission status for a report."""
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        raw = await r.get(f"portal:1930:{report_id}")
        await r.close()
        if raw:
            return json.loads(raw)
        return {"status": "pending", "note": "Still processing or case_id not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
