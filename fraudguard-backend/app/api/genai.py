from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/genai", tags=["Generative AI"])

class ThreatBriefRequest(BaseModel):
    tx_id: str
    amount: int
    risk_score: float
    modalities_flagged: list[str]

@router.post("/threat-brief")
async def generate_threat_brief(req: ThreatBriefRequest):
    """
    Simulates sending the raw risk evaluation to an LLM (e.g. Gemini/GPT) 
    and returning a human-readable threat brief.
    """
    if req.risk_score > 70:
        brief = (f"This transaction exhibits the classic symptoms of the 'Jamtara Urgent Utility' fraud vector. "
                 f"The analysis flagged the {', '.join(req.modalities_flagged)} modalities as highly suspicious. "
                 f"The user is being asked to transfer INR {req.amount} rapidly to a known mule ring. "
                 f"Immediate Account hold recommended.")
    elif req.risk_score > 40:
        brief = (f"Transaction matches some automated phishing characteristics via {', '.join(req.modalities_flagged)}, "
                 f"but lacks definitive malicious payload confirmation. A manual review or 2FA step-up is required.")
    else:
        brief = (f"Transaction appears routine. The requested INR {req.amount} transfer aligns with standard "
                 f"baseline behaviors. Minimal risk detected.")
                 
    return {
        "status": "SUCCESS",
        "generated_brief": brief
    }
