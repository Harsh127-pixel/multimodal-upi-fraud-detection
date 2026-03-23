import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RiskAggregator:
    def __init__(self):
        # Weights for different modalities
        self.WEIGHTS = {
            "transaction": 0.5,
            "sms": 0.25,
            "voice": 0.25
        }

    def aggregate(self, 
                  tx_score: float, 
                  sms_confidence: Optional[float] = None, 
                  voice_confidence: Optional[float] = None) -> Dict:
        """
        Combines scores from different modalities into a single risk profile.
        Score range: 0-100
        """
        total_weight = self.WEIGHTS["transaction"]
        weighted_score = tx_score * self.WEIGHTS["transaction"]
        
        modalities = ["transaction"]
        
        if sms_confidence is not None:
            weighted_score += (sms_confidence * 100) * self.WEIGHTS["sms"]
            total_weight += self.WEIGHTS["sms"]
            modalities.append("sms")
            
        if voice_confidence is not None:
            weighted_score += (voice_confidence * 100) * self.WEIGHTS["voice"]
            total_weight += self.WEIGHTS["voice"]
            modalities.append("voice")
            
        final_score = weighted_score / total_weight if total_weight > 0 else 0
        
        risk_level = "LOW"
        if final_score >= 75:
            risk_level = "CRITICAL"
        elif final_score >= 40:
            risk_level = "MEDIUM"
            
        return {
            "global_score": round(final_score, 1),
            "risk_level": risk_level,
            "modalities_analyzed": modalities,
            "timestamp": datetime.now().isoformat(),
            "recommendation": self._get_recommendation(final_score, modalities)
        }

    def _get_recommendation(self, score: float, modalities: List[str]) -> str:
        if score >= 75:
            return "IMMEDIATE BLOCK: High correlation across multiple fraud vectors."
        if score >= 40:
            return "CAUTION: Suspicious activity detected. Manual verification recommended."
        return "SAFE: No significant risk patterns identified."

aggregator = RiskAggregator()
