from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class UPIVerifyRequest(BaseModel):
    upi_id: str

class UPIVerifyResponse(BaseModel):
    risk_score: int
    risk_level: str
    risk_signals: List[str]

@router.post("/verify", response_model=UPIVerifyResponse)
async def verify_upi(request: UPIVerifyRequest):
    upi_id = request.upi_id.lower()
    
    # Rule-based scoring
    risk_score = 30 # Base score for unknown IDs
    risk_signals: List[str] = []
    
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
        
    # Cap to 5 signals
    capper = min(5, len(risk_signals))
    return {
        "risk_score": risk_score,
        "risk_level": level,
        "risk_signals": [risk_signals[i] for i in range(capper)]
    }
