import os
import requests
import json
import numpy as np
import librosa
from app.workers.celery_app import celery_app
from app.ml.call_intent import CallIntentClassifier

@celery_app.task(name="app.workers.audio_task.analyze_audio")
def analyze_audio(file_path: str):
    """
    Analyzes audio for deepfake detection and fraud intent.
    """
    try:
        # Step 1 — M5 (AASIST) Deepfake Detection
        is_synthetic = False
        confidence = 0.65
        detection_method = "m5_aasist_local" # Simulated on-device AASIST Q8
        
        resemble_api_key = os.getenv("RESEMBLE_API_KEY")
        if resemble_api_key:
            try:
                with open(file_path, "rb") as f:
                    files = {"file": f}
                    response = requests.post(
                        "https://detect.resemble.ai/api/v1/projects",
                        headers={"Authorization": f"Token {resemble_api_key}"},
                        files=files,
                        timeout=30
                    )
                    if response.status_code == 200:
                        data = response.json()
                        is_synthetic = data.get("is_synthetic", False)
                        confidence = float(data.get("confidence", 0.8))
                        detection_method = "resemble_ai_cloud"
            except Exception:
                pass

        if detection_method == "m5_aasist_local":
            # Real AASIST (on-device) would process the raw waveform.
            # Here we simulate feature extraction used by AASIST.
            y, sr = librosa.load(file_path, sr=None)
            # Simulated feature: spectral centroid and zero crossing rate variance
            sc = librosa.feature.spectral_centroid(y=y, sr=sr)
            zcr = librosa.feature.zero_crossing_rate(y=y)
            # Synthetic voices often have unnaturally consistent ZCR or Centroid "shimmer"
            shimmer = np.std(sc) / np.mean(sc)
            zcr_var = np.var(zcr)
            
            # Simple simulation logic for deepfake detection
            is_synthetic = (shimmer < 0.1) or (zcr_var < 0.0001)
            confidence = 0.88 if is_synthetic else 0.74

        # Step 2 — Transcript + intent analysis (M4)
        from app.ml.model_registry import registry
        clf = registry.get_m4_classifier()  # Use registry for singleton
        
        transcript = clf.transcribe(file_path)
        intent_result = clf.classify_transcript(transcript)
        
        detected_patterns = intent_result.get("detected_patterns", [])
        highest_risk_pattern = intent_result.get("highest_risk_pattern", "")
        intent_confidence = intent_result.get("confidence", 0.0)

        # Step 3 — Compute combined risk score
        base = 75 if is_synthetic else 10
        pattern_bonus = {
            "urgency": 20, 
            "threat": 20, 
            "money_request": 15, 
            "impersonation": 15, 
            "secrecy_demand": 10
        }
        
        combined_score = min(100, base + sum([pattern_bonus.get(p, 0) for p in detected_patterns]))
        risk_level = "high" if combined_score >= 70 else "medium" if combined_score >= 40 else "low"

        # Result dict
        result = {
            "is_synthetic": is_synthetic,
            "deepfake_confidence": float(confidence),
            "detection_method": detection_method,
            "transcript": transcript,
            "detected_patterns": detected_patterns,
            "highest_risk_pattern": highest_risk_pattern,
            "intent_confidence": float(intent_confidence),
            "combined_risk_score": int(combined_score),
            "risk_level": risk_level,
            "model_m5": "AASIST Q8 INT8 (Simulated)",
            "model_m4": "DistilRoBERTa Intent"
        }
        return result

    except Exception as e:
        return {"error": str(e)}
    finally:
        # Step 4 — Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)
