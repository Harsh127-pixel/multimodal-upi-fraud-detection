import torch
import torch.nn.functional as F
import os
import json
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger(__name__)

class CallIntentClassifier:
    LABEL_MAP = {0: "urgency", 1: "impersonation", 2: "money_request", 3: "secrecy_demand", 4: "threat"}
    
    def __init__(self, model_dir="models/m4_intent_classifier"):
        self.model_dir = model_dir
        self.tokenizer = None
        self.model = None
        self.whisper_model = None
        self._load_models()

    def _load_models(self):
        try:
            logger.info(f"Loading M4 intent classifier from {self.model_dir}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_dir)
            self.model.eval()
            
            # Label map might provide actual string names if needed
            label_map_path = os.path.join(self.model_dir, "label_map.json")
            if os.path.exists(label_map_path):
                with open(label_map_path, "r") as f:
                    data = json.load(f)
                    self.LABEL_MAP = {int(k): v for k, v in data.items()}
        except Exception as e:
            logger.error(f"Error loading M4 models: {e}")
            # We don't raise here to allow ModelRegistry to handle it or lazy load later?
            # Actually, P13 prompt says "Add get_m4_classifier() to ModelRegistry with lazy-load"

    def transcribe(self, audio_path: str) -> str:
        """Transcribes audio using OpenAI Whisper base model."""
        import whisper
        if self.whisper_model is None:
            logger.info("Loading Whisper base model...")
            self.whisper_model = whisper.load_model("base")
        
        try:
            # language=None triggers auto-detection for Hindi/English
            result = self.whisper_model.transcribe(audio_path, language=None)
            return result["text"]
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            if "ffmpeg" in str(e).lower():
                raise RuntimeError("ffmpeg not found! Whisper requires ffmpeg installed on the system.")
            raise e

    def classify_transcript(self, transcript: str) -> dict:
        """Classifies transcript text into fraud patterns."""
        # Keyword-based pattern matching fallback
        patterns = {
            "urgency": ["turant", "abhi", "jaldi", "immediate", "urgent", "expire"],
            "impersonation": ["manager", "officer", "bank", "police", "service", "kyc"],
            "money_request": ["transfer", "bhejo", "send", "pay", "baaki", "lottery", "prize"],
            "secrecy_demand": ["secret", "don't tell", "kisi ko mat batana", "otp"],
            "threat": ["block", "freeze", "jail", "legal", "action"]
        }

        detected_patterns = []
        text_lower = transcript.lower()
        for label, keywords in patterns.items():
            if any(kw.lower() in text_lower for kw in keywords):
                detected_patterns.append(label)

        if self.tokenizer is None or self.model is None:
            logger.warning("M4 Intent Classifier models not loaded, using patterns only.")
            confidence_val = 0.85 if detected_patterns else 0.1
            top_label = detected_patterns[0] if detected_patterns else "safe"
            
            return {
                "detected_patterns": detected_patterns or ["safe"],
                "highest_risk_pattern": top_label,
                "confidence": confidence_val,
                "risk_level": "HIGH" if detected_patterns else "LOW"
            }

        inputs = self.tokenizer(
            transcript, 
            padding="max_length", 
            truncation=True, 
            max_length=128, 
            return_tensors="pt"
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            scores = F.softmax(outputs.logits, dim=1)
            confidence, predicted_idx = torch.max(scores, dim=1)
            
            top_label = self.LABEL_MAP.get(predicted_idx.item(), "unknown")
            confidence_val = float(confidence.item())
            
            # Combine BERT with patterns
            final_patterns = list(set([top_label] + detected_patterns))
            if confidence_val < 0.5 and detected_patterns:
                confidence_val = 0.6 # Boost if patterns match but BERT is unsure
            
            return {
                "detected_patterns": final_patterns,
                "highest_risk_pattern": top_label,
                "confidence": confidence_val,
                "risk_level": "HIGH" if confidence_val > 0.7 else "MEDIUM"
            }

    def analyze(self, audio_path: str) -> dict:
        """Full pipeline: Audio -> Transcript -> Intent Classification."""
        transcript = self.transcribe(audio_path)
        result = self.classify_transcript(transcript)
        return {"transcript": transcript, **result}
