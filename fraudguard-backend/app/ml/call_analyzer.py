import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import logging

logger = logging.getLogger(__name__)

class CallAnalyzer:
    def __init__(self, model_path="models/m4_call_analyzer"):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Consistent with Training script
        self.LABELS = ["urgency", "impersonation", "money_request", "secrecy_demand", "threat"]

    def _load_model(self):
        if self.model is None:
            if not os.path.exists(self.model_path):
                raise RuntimeError(f"M4 model not found at {self.model_path}. Run ml_training/train_m4_calls.py first.")
            
            logger.info(f"Loading M4 Call Analyzer from {self.model_path}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()

    def analyze(self, transcript: str) -> dict:
        self._load_model()
        
        inputs = self.tokenizer(transcript, return_tensors="pt", truncation=True, max_length=128, padding=True).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            confidence, prediction_idx = torch.max(probs, dim=-1)
            
        pattern = self.LABELS[prediction_idx.item()]
        
        return {
            "fraud_pattern": pattern,
            "confidence": float(confidence.item()),
            "transcript_preview": transcript[:50] + "..." if len(transcript) > 50 else transcript,
            "is_suspicious": True # Call transcripts in this context are generated from suspicious patterns
        }
