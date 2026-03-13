# ─────────────────────────────────────────────
# utils.py — Real-Time Scam Detection Utilities
# ─────────────────────────────────────────────

# High-risk UPI scam keywords commonly used by scammers during calls
SCAM_KEYWORDS = [
    # Urgency triggers
    "urgent", "immediately", "right now", "don't delay", "emergency",
    # OTP / PIN related
    "share your otp", "tell me your otp", "otp", "pin", "cvv",
    "share your pin", "enter your pin", "bank pin",
    # UPI specific
    "upi id", "google pay", "phonepe", "paytm", "send money",
    "transfer money", "pay now", "request money",
    # Authority impersonation
    "rrbi", "income tax", "police", "cyber crime", "government",
    "court notice", "arrest warrant", "account blocked",
    # Reward / lottery
    "you have won", "lottery", "prize", "reward", "cashback offer",
    "claim now", "selected", "lucky winner",
    # Fear tactics
    "account will be closed", "account suspended", "blocked",
    "verify your account", "kyc pending", "kyc expired",
]

def detect_scam_keywords(transcript: str) -> dict:
    """
    Scans a transcribed call text for known UPI scam keywords.
    
    Args:
        transcript (str): Transcribed speech from the live audio stream.
        
    Returns:
        dict: Contains list of matched keywords and overall scam_detected flag.
    """
    transcript_lower = transcript.lower()
    
    matched_keywords = [
        keyword for keyword in SCAM_KEYWORDS
        if keyword in transcript_lower
    ]
    
    scam_detected = len(matched_keywords) > 0
    
    return {
        "scam_detected": scam_detected,
        "matched_keywords": matched_keywords,
        "keyword_count": len(matched_keywords),
        "risk_level": "HIGH" if len(matched_keywords) >= 3 else "MEDIUM" if len(matched_keywords) >= 1 else "LOW"
    }


def build_alert(voice_score: float, keyword_result: dict) -> dict:
    """
    Combines deepfake voice detection and keyword analysis into a final user alert.
    
    Args:
        voice_score (float): Real voice probability from the model (0 = fake, 1 = real)
        keyword_result (dict): Result from detect_scam_keywords()
        
    Returns:
        dict: Final alert object to be sent to the user in real-time.
    """
    alert_messages = []
    is_scam = False

    # Voice deepfake alert
    if voice_score < 0.5:
        alert_messages.append("⚠️ Caller voice appears to be synthetic (AI-generated).")
        is_scam = True

    # Keyword alert
    if keyword_result["scam_detected"]:
        alert_messages.append(
            f"⚠️ Possible UPI scam detected. Suspicious phrases heard: "
            f"{', '.join(keyword_result['matched_keywords'][:3])}"  # Show top 3 keywords
        )
        is_scam = True

    if not is_scam:
        alert_messages.append("✅ No scam signals detected in this call segment.")

    return {
        "is_scam": is_scam,
        "alert_messages": alert_messages,
        "voice_authenticity_score": voice_score,
        "keyword_risk_level": keyword_result["risk_level"],
        "matched_keywords": keyword_result["matched_keywords"]
    }
