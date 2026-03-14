import re

AUTHORITY_KEYWORDS = [
    "bank",
    "rbi",
    "government",
    "income tax",
    "verification",
    "otp",
    "account blocked",
    "bank officer",
    "kyc"
]

def detect_impersonation(text: str):

    text = text.lower()

    detected_keywords = []

    for keyword in AUTHORITY_KEYWORDS:
        if re.search(keyword, text):
            detected_keywords.append(keyword)

    score = len(detected_keywords) / len(AUTHORITY_KEYWORDS)

    return {
        "impersonation_detected": score > 0,
        "scam_probability": round(score, 2),
        "detected_keywords": detected_keywords
    }

AUTHORITY_KEYWORDS = [
    "bank",
    "rbi",
    "government",
    "income tax",
    "verification",
    "otp",
    "account blocked",
    "bank officer",
    "kyc"
]

def detect_impersonation(text: str):

    text = text.lower()

    detected_keywords = []

    for keyword in AUTHORITY_KEYWORDS:
        if re.search(keyword, text):
            detected_keywords.append(keyword)

    score = len(detected_keywords) / len(AUTHORITY_KEYWORDS)

    return {
        "impersonation_detected": score > 0,
        "scam_probability": round(score, 2),
        "detected_keywords": detected_keywords
    }