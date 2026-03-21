from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ml.model_registry import registry

router = APIRouter()

class SMSRequest(BaseModel):
    text: str

@router.post("/analyze")
async def analyze_sms(request: SMSRequest):
    try:
        classifier = registry.get_m3_classifier()
        result = classifier.classify(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
