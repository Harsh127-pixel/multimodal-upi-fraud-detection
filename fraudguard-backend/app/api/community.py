from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import random
import uuid

router = APIRouter(prefix="/community", tags=["Community Watch"])

class OCRReportRequest(BaseModel):
    image_base64: str
    description: Optional[str] = ""

@router.post("/report")
async def process_community_report(req: OCRReportRequest):
    """
    Simulates receiving a screenshot of a scam (e.g. WhatsApp spam),
    running OCR via GenAI vision models, and extracting threat indicators.
    """
    # Simulate OCR Extraction
    extracted_text = "Urgent! Your electricity bill is due tonight at 9 PM. Update KYC immediately or power will be disconnected. Call +919876543210 or pay at http://fake-elect-bill.xyz"
    
    indicators = [
        {"type": "phone", "value": "+919876543210"},
        {"type": "url", "value": "http://fake-elect-bill.xyz"}
    ]
    
    # Automatically add to Honeypot / Blacklist (Simulated)
    # Redis integration would happen here
    
    return {
        "status": "PROCESSED",
        "report_id": str(uuid.uuid4()),
        "extracted_text": extracted_text,
        "threat_indicators_found": indicators,
        "action": "Ingested into Global Threat Matrix",
        "reward_points": 50
    }
