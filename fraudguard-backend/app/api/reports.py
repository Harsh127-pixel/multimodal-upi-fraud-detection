from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import os
import json
import redis.asyncio as redis

from app.core.database import get_db
from app.models.fraud_report import FraudReport
from app.models.upi_profile import UPIProfile

router = APIRouter()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

class FraudReportRequest(BaseModel):
    upi_id: str
    fraud_type: str  # fake_qr | impersonation | lottery | investment | other
    amount_lost: float
    utr_number: str
    description: str
    evidence_url: Optional[str] = None

@router.post("/submit")
async def submit_report(request: FraudReportRequest, db: AsyncSession = Depends(get_db)):
    # 1. Save to FraudReport table
    report = FraudReport(
        upi_id=request.upi_id,
        fraud_type=request.fraud_type,
        amount=request.amount_lost,
        utr_number=request.utr_number,
        description=request.description,
        evidence_url=request.evidence_url
    )
    db.add(report)
    
    # 2. Upsert UPIProfile
    stmt = select(UPIProfile).where(UPIProfile.upi_id == request.upi_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if profile:
        profile.fraud_count += 1
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
    
    # 3. Add to Redis Set "community_blacklist"
    r = redis.from_url(REDIS_URL, decode_responses=True)
    await r.sadd("community_blacklist", request.upi_id)
    
    # 4. Publish to Redis channel "community_updates"
    update_msg = {
        "type": "new_report",
        "upi_id": request.upi_id,
        "fraud_type": request.fraud_type
    }
    await r.publish("community_updates", json.dumps(update_msg))
    await r.close()
    
    return {
        "message": "Report submitted",
        "case_id": str(report.id),
        "upi_id": request.upi_id,
        "blacklisted": profile.blacklisted
    }

@router.get("/blacklist")
async def get_blacklist():
    r = redis.from_url(REDIS_URL, decode_responses=True)
    count = await r.scard("community_blacklist")
    # Using SSCAN to get items as requested. 
    # SSCAN returns [cursor, [items]]
    _, recent = await r.sscan("community_blacklist", count=10)
    await r.close()
    return {
        "count": count,
        "recent": recent
    }
