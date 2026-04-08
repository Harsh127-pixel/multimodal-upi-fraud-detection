"""
FraudGuard Intelligence Engine
Covers: Velocity Profiling, Geo-Velocity (Impossible Travel), App Integrity,
        Behavioral Biometrics, Dark Web Monitor, Multilingual NLP expansion
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
import math, random, hashlib
from datetime import datetime, timezone

router = APIRouter(prefix="/intelligence", tags=["Intelligence Engine"])

# ─── In-memory stores (prototype) ────────────────────────────────────────────
VELOCITY_STORE: dict = {}        # payer_upi -> list of (timestamp, amount)
GEO_HISTORY: dict = {}           # payer_upi -> (lat, lng, timestamp)
DARKWEB_KNOWN: set = {           # Simulated dark-web leak database
    "+919876543210", "scammer@upi", "fraudster@upi", "fakekyc@okaxis",
    "lotteryprize@ybl", "helpdesk.sbi99@upi", "refund.paytm99@upi"
}

# ─── Hinglish/Hindi fraud keyword library (M3/M4 expansion) ─────────────────
HINGLISH_PATTERNS = {
    "aapka account band ho jayega": "Account block threat",
    "ek baar otp bata do": "OTP harvesting",
    "ek baar otp share karo": "OTP harvesting",
    "kyc update karo": "KYC impersonation",
    "abhi transfer karo": "Urgency pressure",
    "aaj raat tak": "Deadline pressure",
    "refund mil jayega": "Refund lure",
    "lottery jeeti hai": "Prize lure",
    "kisi ko mat batana": "Secrecy demand",
    "bank officer bol raha hoon": "Impersonation - Bank",
    "police case ho jayega": "Legal threat",
    "aapka number block hoga": "Account block threat",
    "gift card kharido": "Gift card scam",
    "insurance premium": "Insurance fraud",
    "mutual fund update": "Investment fraud",
}

# ─── MODELS ──────────────────────────────────────────────────────────────────

class VelocityRequest(BaseModel):
    payer_upi: str
    amount: float
    timestamp: str = ""

class GeoVelocityRequest(BaseModel):
    payer_upi: str
    lat: float
    lng: float
    timestamp: str = ""

class BiometricRequest(BaseModel):
    user_id: str
    dwell_times: List[float]     # ms each key held
    flight_times: List[float]    # ms between keys
    expected_dwell_mean: Optional[float] = None   # stored baseline
    expected_flight_mean: Optional[float] = None

class AppIntegrityRequest(BaseModel):
    device_id: str
    is_emulator: bool = False
    is_repackaged_apk: bool = False
    screen_capture_active: bool = False
    debug_mode_on: bool = False

class DarkWebRequest(BaseModel):
    upi_id: Optional[str] = None
    phone: Optional[str] = None

class HinglishNLPRequest(BaseModel):
    text: str

# ─── ENDPOINTS ─────────────────────────────────────────────────────────────

@router.post("/velocity/check")
async def check_velocity(req: VelocityRequest):
    """Sliding window velocity check: flags sudden spikes in tx amount/frequency."""
    history = VELOCITY_STORE.get(req.payer_upi, [])
    history.append({"amount": req.amount, "ts": req.timestamp or datetime.now(timezone.utc).isoformat()})
    VELOCITY_STORE[req.payer_upi] = history[-20:]  # Keep last 20

    avg = sum(h["amount"] for h in history) / len(history) if history else 0
    spike_ratio = req.amount / avg if avg > 0 else 1.0
    
    is_spike = spike_ratio > 5.0
    return {
        "user": req.payer_upi,
        "current_amount": req.amount,
        "historical_avg": round(avg, 2),
        "spike_ratio": round(spike_ratio, 2),
        "velocity_alert": is_spike,
        "risk_boost": 30.0 if is_spike else 0.0,
        "message": f"Spike detected: {spike_ratio:.1f}x above baseline" if is_spike else "Normal velocity"
    }


@router.post("/geo/check")
async def check_geo_velocity(req: GeoVelocityRequest):
    """Impossible Travel detection: flags physically impossible location jumps."""
    prev = GEO_HISTORY.get(req.payer_upi)
    now_ts = datetime.now(timezone.utc)
    GEO_HISTORY[req.payer_upi] = {"lat": req.lat, "lng": req.lng, "ts": now_ts.isoformat()}

    if not prev:
        return {"impossible_travel": False, "message": "First location recorded"}

    # Haversine distance in km
    R = 6371
    dlat = math.radians(req.lat - prev["lat"])
    dlng = math.radians(req.lng - prev["lng"])
    a = math.sin(dlat/2)**2 + math.cos(math.radians(prev["lat"])) * math.cos(math.radians(req.lat)) * math.sin(dlng/2)**2
    dist_km = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # Speed in km/h: assume 15 minutes between txns (worst-case suspicious scenario)
    speed_kmh = dist_km / 0.25
    is_impossible = speed_kmh > 800  # Faster than commercial flight

    return {
        "impossible_travel": is_impossible,
        "distance_km": round(dist_km, 1),
        "estimated_speed_kmh": round(speed_kmh, 1),
        "risk_boost": 45.0 if is_impossible else 0.0,
        "message": f"IMPOSSIBLE TRAVEL: {dist_km:.0f}km in ~15min (speed: {speed_kmh:.0f} km/h)" if is_impossible else "Location within normal range"
    }


@router.post("/biometrics/verify")
async def verify_biometrics(req: BiometricRequest):
    """UPI PIN keystroke dynamics — verifies typing rhythm matches baseline."""
    if not req.dwell_times or not req.flight_times:
        return {"match": True, "confidence": 0.5, "message": "Insufficient data"}

    dwell_mean = sum(req.dwell_times) / len(req.dwell_times)
    flight_mean = sum(req.flight_times) / len(req.flight_times)

    # Compare with baseline if provided
    if req.expected_dwell_mean and req.expected_flight_mean:
        dwell_dev = abs(dwell_mean - req.expected_dwell_mean) / (req.expected_dwell_mean + 1)
        flight_dev = abs(flight_mean - req.expected_flight_mean) / (req.expected_flight_mean + 1)
        anomaly_score = (dwell_dev + flight_dev) / 2
        is_match = anomaly_score < 0.4
    else:
        anomaly_score = 0.1
        is_match = True

    return {
        "match": is_match,
        "anomaly_score": round(anomaly_score, 3),
        "risk_boost": 35.0 if not is_match else 0.0,
        "dwell_mean_ms": round(dwell_mean, 2),
        "flight_mean_ms": round(flight_mean, 2),
        "message": "Rhythm mismatch — potential device takeover" if not is_match else "Typing rhythm verified"
    }


@router.post("/app/integrity")
async def check_app_integrity(req: AppIntegrityRequest):
    """Checks if the UPI app environment has been tampered with."""
    threats = []
    score_penalty = 0

    if req.is_emulator:
        threats.append("Running on emulator — automated scripting risk")
        score_penalty += 40
    if req.is_repackaged_apk:
        threats.append("APK repackaged/tampered — malicious overlay injection likely")
        score_penalty += 50
    if req.screen_capture_active:
        threats.append("Screen capture tool active during payment")
        score_penalty += 30
    if req.debug_mode_on:
        threats.append("Debug mode enabled — reverse engineering risk")
        score_penalty += 20

    return {
        "device_id": req.device_id,
        "integrity_passed": len(threats) == 0,
        "threats": threats,
        "risk_boost": score_penalty,
        "verdict": "TAMPERED" if threats else "VERIFIED"
    }


@router.post("/darkweb/scan")
async def scan_darkweb(req: DarkWebRequest):
    """Checks UPI ID/phone number against simulated dark-web leak database."""
    found_leaks = []

    if req.upi_id and req.upi_id in DARKWEB_KNOWN:
        found_leaks.append({"type": "UPI", "value": req.upi_id, "source": "Telegram Fraud Kit #4812"})

    if req.phone and req.phone in DARKWEB_KNOWN:
        found_leaks.append({"type": "Phone", "value": req.phone, "source": "Dark Web Marketplace"})

    return {
        "leaks_found": len(found_leaks),
        "entries": found_leaks,
        "risk_boost": 60.0 if found_leaks else 0.0,
        "verdict": "COMPROMISED" if found_leaks else "CLEAN",
        "last_checked": datetime.now(timezone.utc).isoformat()
    }


@router.post("/nlp/hinglish")
async def analyze_hinglish(req: HinglishNLPRequest):
    """Multilingual NLP: detects Hinglish/Hindi scam patterns."""
    text_lower = req.text.lower()
    matched = []
    for phrase, label in HINGLISH_PATTERNS.items():
        if phrase in text_lower:
            matched.append({"phrase": phrase, "type": label})

    confidence = min(0.95, 0.4 + (len(matched) * 0.2)) if matched else 0.05
    return {
        "is_fraud": len(matched) > 0,
        "matched_patterns": matched,
        "confidence": confidence,
        "language_detected": "Hinglish/Hindi",
        "risk_boost": 25.0 * len(matched)
    }
