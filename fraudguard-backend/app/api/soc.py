"""
FraudGuard SOC Dashboard API
Live metrics for Security Operations Center view.
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import random

router = APIRouter(prefix="/soc", tags=["SOC Dashboard"])

# Simulated counters that persist in-memory for the session
_SOC_STATE = {
    "blocked_today": 127,
    "allowed_today": 8943,
    "honeypot_hits": 14,
    "active_cases": 6,
    "darkweb_alerts": 3
}

@router.get("/metrics")
async def get_soc_metrics():
    """Returns live SOC metrics for dashboard display."""
    # Simulate live fluctuation
    _SOC_STATE["allowed_today"] += random.randint(0, 3)
    
    total = _SOC_STATE["blocked_today"] + _SOC_STATE["allowed_today"]
    block_rate = (_SOC_STATE["blocked_today"] / total * 100) if total > 0 else 0

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "blocked_today": _SOC_STATE["blocked_today"],
        "allowed_today": _SOC_STATE["allowed_today"],
        "block_rate_pct": round(block_rate, 2),
        "honeypot_hits_today": _SOC_STATE["honeypot_hits"],
        "active_cases": _SOC_STATE["active_cases"],
        "darkweb_alerts": _SOC_STATE["darkweb_alerts"],
        "uptime_pct": 99.97,
        "avg_response_ms": random.randint(22, 48)
    }

@router.get("/heatmap")
async def get_transaction_heatmap():
    """Returns hourly transaction risk distribution for heatmap."""
    INDIA_CITIES = [
        ("Mumbai", 19.07, 72.87), ("Delhi", 28.61, 77.20),
        ("Bangalore", 12.97, 77.59), ("Hyderabad", 17.38, 78.48),
        ("Chennai", 13.08, 80.27), ("Kolkata", 22.57, 88.36),
        ("Pune", 18.52, 73.86), ("Jaipur", 26.91, 75.79),
        ("Lucknow", 26.85, 80.95), ("Ahmedabad", 23.02, 72.57),
    ]
    
    points = []
    for city, lat, lng in INDIA_CITIES:
        points.append({
            "city": city,
            "lat": lat,
            "lng": lng,
            "tx_count": random.randint(50, 800),
            "fraud_count": random.randint(1, 20),
            "risk_level": random.choice(["LOW", "LOW", "MEDIUM", "HIGH"])
        })

    return {"points": points, "generated_at": datetime.now(timezone.utc).isoformat()}

@router.get("/top-threats")
async def get_top_threats():
    """Returns top 5 most targeted UPI IDs and threat actors."""
    threats = [
        {"rank": 1, "upi_id": "helpdesk.sbi99@upi", "hits": 47, "type": "Impersonation", "status": "BLACKLISTED"},
        {"rank": 2, "upi_id": "refund.paytm99@upi", "hits": 32, "type": "Refund Scam", "status": "BLACKLISTED"},
        {"rank": 3, "upi_id": "lotteryprize@ybl", "hits": 28, "type": "Prize Lure", "status": "BLACKLISTED"},
        {"rank": 4, "upi_id": "fakekyc@okaxis", "hits": 19, "type": "KYC Fraud", "status": "MONITORING"},
        {"rank": 5, "upi_id": "charity_fake@upi", "hits": 11, "type": "Donation Scam", "status": "MONITORING"},
    ]
    return {"threats": threats}

@router.get("/timeline/{tx_id}")
async def get_fraud_timeline(tx_id: str):
    """Reconstructs the fraud event timeline for a given transaction."""
    base_time = datetime.now(timezone.utc)
    
    events = [
        {
            "offset_min": -8,
            "event": "Suspicious SMS received",
            "detail": "\"Your electricity connection will be cut tonight. Pay ₹499 immediately.\"",
            "severity": "WARN",
            "icon": "sms",
            "detected_by": "M3-SMS-BERT"
        },
        {
            "offset_min": -5,
            "event": "Unknown call received",
            "detail": "Caller ID: +919876543210 (Known vishing number)",
            "severity": "HIGH",
            "icon": "call",
            "detected_by": "Call Interceptor"
        },
        {
            "offset_min": -2,
            "event": "Accessibility service triggered",
            "detail": "Auto-clicker malware attempted to invoke UPI app",
            "severity": "CRITICAL",
            "icon": "touch_app",
            "detected_by": "Mobile Device Telemetry"
        },
        {
            "offset_min": 0,
            "event": f"Payment attempt: ₹50,000 to scammer@upi",
            "detail": f"TX-ID: {tx_id} — Post-call transaction matches CTC pattern",
            "severity": "CRITICAL",
            "icon": "payment",
            "detected_by": "M1 + CTC Engine"
        },
        {
            "offset_min": 0,
            "event": "Transaction BLOCKED",
            "detail": "Risk Score: 94.5 — FraudGuard intervention successful",
            "severity": "SUCCESS",
            "icon": "shield",
            "detected_by": "Risk Aggregator"
        }
    ]

    return {
        "tx_id": tx_id,
        "timeline": events,
        "total_events": len(events),
        "outcome": "BLOCKED",
        "funds_saved": 50000
    }
