# Risk fusion engine logic
def calculate_risk_score(voice_confidence: float, text_flag: bool) -> dict:
    risk_score = 0.0
    
    if text_flag:
        risk_score += 0.5
        
    if voice_confidence > 0.8:
        risk_score += 0.5
        
    level = "High" if risk_score >= 0.8 else "Medium" if risk_score > 0.3 else "Low"
    
    return {
        "score": risk_score,
        "level": level
    }
