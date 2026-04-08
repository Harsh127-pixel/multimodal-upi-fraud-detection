from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.ml.model_registry import registry
from app.ml.risk_aggregator import aggregator
from app.api.transactions import TransactionRequest
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class MultimodalVerifyRequest(BaseModel):
    transaction: Optional[TransactionRequest] = None
    sms_text: Optional[str] = None
    call_transcript: Optional[str] = None

@router.post("/verify")
async def multimodal_verify(request: MultimodalVerifyRequest):
    tx_score = 0.0
    sms_confidence = None
    voice_confidence = None
    
    # 1. Score Transaction
    if request.transaction:
        try:
            from app.ml.feature_eng import FeatureExtractor
            from app.api.transactions import _check_ctc_signal
            
            # Check CTC signal (5-min window)
            ctc_flag, ctc_signal = await _check_ctc_signal(request.transaction.payer_upi_id)
            is_post_call = request.transaction.is_post_call or ctc_flag
            
            tx_dict = request.transaction.model_dump()
            tx_dict["is_post_call"] = is_post_call
            
            extractor = FeatureExtractor()
            features = extractor.extract(tx_dict).reshape(1, -1)
            m1 = registry.get_m1_scorer()
            tx_score = float(m1.predict_proba(features)[0][1] * 100)
            
            # Deterministic Blacklist Override
            known_scammers = ["scammer@upi", "fraudster@upi", "fake_charity@ybl"]
            if request.transaction.upi_id in known_scammers:
                tx_score = max(tx_score, 94.5)
                
            # Heuristic High-Value Override
            if request.transaction.amount > 20000 and request.transaction.is_post_call:
                tx_score = max(tx_score, 88.0)
                
        except Exception as e:
            logger.error(f"Multimodal M1 Score error: {e}")
            tx_score = 0.0

    # 2. Analyze SMS
    if request.sms_text:
        try:
            m3 = registry.get_m3_classifier()
            sms_res = m3.classify(request.sms_text)
            # If it predicted SAFE, we use a low score; if FRAUD, we use high score
            sms_confidence = sms_res["confidence"] if sms_res["is_fraud"] else (1.0 - sms_res["confidence"])
        except Exception as e:
            print(f"M3 Score error: {e}")

    # 3. Analyze Call
    if request.call_transcript:
        try:
            m4 = registry.get_m4_classifier()
            call_res = m4.classify_transcript(request.call_transcript)
            # Same logic: get risk confidence
            voice_confidence = call_res["confidence"] if call_res["risk_level"] != "LOW" else (1.0 - call_res["confidence"])
        except Exception as e:
            print(f"M4 Score error: {e}")

    # 4. Aggregate
    result = aggregator.aggregate(tx_score, sms_confidence, voice_confidence)
    
    return result
