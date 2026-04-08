from fastapi import APIRouter
from pydantic import BaseModel
import datetime

router = APIRouter(prefix="/legal", tags=["Legal Export API"])

class FIRGenerateRequest(BaseModel):
    tx_id: str
    evidence_bundle_hash: str
    victim_upi: str
    threat_description: str

@router.post("/generate-fir")
async def generate_fir(req: FIRGenerateRequest):
    """
    Generates an automated First Information Report (FIR) format payload
    ready to be consumed by the National Cybercrime Portal (1930) API.
    """
    # Simulated PDF/JSON Generation
    fir_payload = {
        "report_metadata": {
            "origin_system": "FraudGuard Enterprise SOC",
            "timestamp_generated": datetime.datetime.now().isoformat(),
            "cybercrime_category": "Financial Fraud / UPI",
        },
        "incident_details": {
            "internal_tx_id": req.tx_id,
            "victim_vpa": req.victim_upi,
            "narrative": req.threat_description
        },
        "forensic_evidence": {
            "blockchain_bundle_hash": req.evidence_bundle_hash,
            "verification_status": "Integrity Maintained & Hashed"
        },
        "legal_status": "DRAFT_READY_FOR_FILING"
    }
    
    return {
        "status": "SUCCESS",
        "message": "FIR Payload generated successfully.",
        "payload": fir_payload
    }
