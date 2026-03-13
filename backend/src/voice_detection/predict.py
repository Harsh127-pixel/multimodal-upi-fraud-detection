import os
import sys
import tempfile
import torch

# Ensure project root is in path to import ml_models
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from ml_models.voice_detection.predict import VoicePredictor

# Global Predictor Instance (Singleton)
PREDICTOR = None

def get_predictor():
    """
    Singleton pattern to ensure the VoicePredictor is loaded only once.
    """
    global PREDICTOR
    if PREDICTOR is None:
        # Construct path to weights file relative to project root
        weights_path = os.path.join(PROJECT_ROOT, "voice_detection_model.pth")
        PREDICTOR = VoicePredictor(model_path=weights_path)
    return PREDICTOR

def assess_voice_authenticity(audio_bytes, weights_path=None):
    """
    The end-to-end Prediction Pipeline for Voice Deepfake Detection.
    
    1. Audio Bytes -> Temporary Audio File
    2. File Path -> ML Model Prediction (ml_models)
    3. Output -> Authenticity Score & Label 
    """
    
    # Use the singleton predictor
    predictor = get_predictor()
    
    # 1. Save bytes to a temporary file so the extractor can load it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_path = tmp_file.name

    try:
        # 2. Run Inference
        # prob is probability of being 'Fake' (0.0 to 1.0)
        fake_prob, label = predictor.predict(tmp_path)
        
        if fake_prob is None:
            return {
                "success": False,
                "error": label # label contains the error message in this case
            }

        # 3. Format Output
        # backend expects real_probability
        real_prob = 1.0 - fake_prob
        
        return {
            "success": True,
            "label": label, # "Fake Voice" or "Real Voice"
            "is_real_probability": round(real_prob, 4),
            "is_fake_probability": round(fake_prob, 4)
        }

    finally:
        # Cleanup temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

