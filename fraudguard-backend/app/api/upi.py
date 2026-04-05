from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List

from app.core.database import get_db
from app.models.upi_profile import UPIProfile

router = APIRouter()

class UPIVerifyRequest(BaseModel):
    upi_id: str

class UPIVerifyResponse(BaseModel):
    risk_score: int
    risk_level: str
    risk_signals: List[str]

@router.post("/verify", response_model=UPIVerifyResponse)
async def verify_upi(request: UPIVerifyRequest, db: AsyncSession = Depends(get_db)):
    upi_id = request.upi_id.lower()
    
    # Check database for existing profile
    stmt = select(UPIProfile).where(UPIProfile.upi_id == upi_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    
    # Rule-based scoring
    risk_score = 30 # Base score for unknown IDs
    risk_signals: List[str] = []
    
    if profile:
        if profile.fraud_count >= 1:
            # Score jumps to 90+ if reported even once
            risk_score = 92 if profile.fraud_count == 1 else 98
            risk_signals.append(f"Warning: {profile.fraud_count} fraud reports associated with this ID")
            
        if profile.blacklisted:
            risk_score = 100
            risk_signals.append("CRITICAL: This UPI ID is officially blacklisted")
    
    # Legacy rules for demo/testing
    if not profile:
        if "new" in upi_id:
            risk_score += 45
            risk_signals.append("Newly registered UPI ID detected")
            
        if "fraud" in upi_id:
            risk_score += 65
            risk_signals.append("Multiple fraud reports found for this ID")
        elif "suspicious" in upi_id:
            risk_score += 30
            risk_signals.append("Suspicious activity patterns observed")
        
    # Ensure score is within 0-100
    risk_score = min(100, max(0, risk_score))
    
    # Determine risk_level
    if risk_score < 40:
        level = "low"
        if not risk_signals:
            risk_signals.append("No significant risk factors identified")
    elif risk_score < 75:
        level = "medium"
    else:
        level = "high"
        
    return {
        "risk_score": risk_score,
        "risk_level": level,
        "risk_signals": risk_signals[:5]
    }
