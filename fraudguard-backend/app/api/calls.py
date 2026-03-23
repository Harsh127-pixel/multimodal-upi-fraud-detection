from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ml.model_registry import registry

router = APIRouter()

class CallRequest(BaseModel):
    transcript: str

@router.post("/analyze")
async def analyze_call(request: CallRequest):
    try:
        analyzer = registry.get_m4_classifier()
        # CallIntentClassifier has classify_transcript instead of analyze in the new prompt
        # but let's see what I wrote in CallIntentClassifier.
        # I added analyze() to remain compatible with previous turn but prompt said classify_transcript
        result = analyzer.classify_transcript(request.transcript) 
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
