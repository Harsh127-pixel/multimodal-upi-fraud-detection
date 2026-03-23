import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import logging

logger = logging.getLogger(__name__)

class SMSClassifier:
    def __init__(self, model_path="models/m3_sms_classifier"):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Fraud keywords for pattern matching
        self.patterns = {
            "OTP request": ["OTP", "otp"],
            "Account block threat": ["band", "block", "freeze", "kyc"],
            "Prize/reward lure": ["prize", "reward", "jeetein", "gift", "cashback"],
            "Urgency pressure": ["turant", "abhi", "jaldi", "immediate", "urgent"],
            "Impersonation": ["manager", "officer", "bank", "police", "service"],
            "Money transfer request": ["transfer", "bhejo", "send", "pay", "baaki"]
        }

    def _load_model(self):
        if self.model is None:
            if not os.path.exists(self.model_path):
                raise RuntimeError(f"M3 model not found at {self.model_path}. Run ml_training/train_m3_sms.py first.")
            
            logger.info(f"Loading M3 SMS Classifier from {self.model_path}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()

    def classify(self, text: str) -> dict:
        self._load_model()
        
        # 1. BERT classification
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128, padding=True).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            confidence, prediction = torch.max(probs, dim=-1)
            
        is_fraud = bool(prediction.item() == 1)
        
        # 2. Pattern matching
        matched_patterns = []
        text_lower = text.lower()
        for label, keywords in self.patterns.items():
            if any(kw.lower() in text_lower for kw in keywords):
                matched_patterns.append(label)
                
        return {
            "is_fraud": is_fraud,
            "confidence": float(confidence.item()),
            "fraud_patterns": matched_patterns,
            "text_preview": text[:50] + "..." if len(text) > 50 else text
        }

# Singleton instance will be managed by ModelRegistry
