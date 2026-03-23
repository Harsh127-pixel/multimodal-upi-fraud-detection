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
        # Step 1 — Deepfake detection
        is_synthetic = False
        confidence = 0.65
        detection_method = "local_heuristic"
        
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
                        # Extract is_synthetic and confidence based on typical Resemble API response
                        is_synthetic = data.get("is_synthetic", False)
                        confidence = float(data.get("confidence", 0.8))
                        detection_method = "resemble_ai"
            except Exception as e:
                # Fallback to local heuristic on API error
                pass

        if detection_method == "local_heuristic":
            y, sr = librosa.load(file_path, sr=None)
            spectral_flatness = np.mean(librosa.feature.spectral_flatness(y=y))
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Simple heuristic: high flatness (static/synthetic-like) or very short duration
            is_synthetic = (spectral_flatness > 0.3) or (duration < 2.0)
            confidence = 0.72 if is_synthetic else 0.65

        # Step 2 — Transcript + intent analysis
        clf = CallIntentClassifier()
        intent_result = clf.analyze(file_path)
        
        transcript = intent_result.get("transcript", "")
        detected_patterns = intent_result.get("detected_patterns", [])
        highest_risk_pattern = intent_result.get("highest_risk_pattern", "")
        intent_confidence = intent_result.get("confidence", 0.0)

        # Step 3 — Compute combined risk score
        base = 80 if is_synthetic else 20
        pattern_bonus = {
            "urgency": 15, 
            "threat": 15, 
            "money_request": 10, 
            "impersonation": 10, 
            "secrecy_demand": 8
        }
        
        combined_score = min(100, base + pattern_bonus.get(highest_risk_pattern, 0))
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
            "risk_level": risk_level
        }
        return result

    except Exception as e:
        return {"error": str(e)}
    finally:
        # Step 4 — Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)
