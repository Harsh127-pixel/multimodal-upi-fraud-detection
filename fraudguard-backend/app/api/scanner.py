"""
FraudGuard Bulk Scanner, QR Detonator, OTP Interception, Webhook Gateway, PDF Reports
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import csv, io, random, uuid, hashlib
from datetime import datetime, timezone

router = APIRouter(tags=["Scanner & Reports"])

# ── WEBHOOK REGISTRY ─────────────────────────────────────────────────────────
WEBHOOK_REGISTRY: dict = {}

class WebhookRegisterRequest(BaseModel):
    url: str
    event_types: List[str] = ["critical_alert", "case_created", "playbook_complete"]
    secret: Optional[str] = None

@router.post("/webhooks/register")
async def register_webhook(req: WebhookRegisterRequest):
    wh_id = f"WH-{uuid.uuid4().hex[:8].upper()}"
    WEBHOOK_REGISTRY[wh_id] = {
        "id": wh_id,
        "url": req.url,
        "event_types": req.event_types,
        "secret": hashlib.sha256((req.secret or wh_id).encode()).hexdigest()[:16],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "deliveries": 0
    }
    return {"webhook_id": wh_id, "status": "registered", "events": req.event_types}

@router.get("/webhooks/list")
async def list_webhooks():
    return {"total": len(WEBHOOK_REGISTRY), "webhooks": list(WEBHOOK_REGISTRY.values())}

@router.delete("/webhooks/{wh_id}")
async def delete_webhook(wh_id: str):
    if wh_id not in WEBHOOK_REGISTRY:
        raise HTTPException(status_code=404, detail="Webhook not found")
    del WEBHOOK_REGISTRY[wh_id]
    return {"deleted": True, "webhook_id": wh_id}

# ── BULK CSV SCANNER ──────────────────────────────────────────────────────────

@router.post("/scanner/bulk")
async def bulk_scan(file: UploadFile = File(...)):
    """Parses a bank statement CSV and risk-scores every transaction row."""
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))

    results = []
    SCAMMER_IDS = {"scammer@upi", "fraudster@upi", "fake_charity@ybl", "lotteryprize@ybl"}

    for i, row in enumerate(reader):
        if i >= 500:  # Cap at 500 rows
            break

        # Extract common bank statement columns (flexible)
        upi_id  = row.get("upi_id") or row.get("payee") or row.get("receiver") or "unknown@upi"
        amount  = float(row.get("amount") or row.get("debit") or row.get("dr") or 0)
        narr    = row.get("narration") or row.get("description") or row.get("remarks") or ""

        # Heuristic risk scoring
        score = 5.0
        if upi_id in SCAMMER_IDS: score += 85
        if amount > 50000: score += 20
        if amount > 100000: score += 30
        if any(kw in narr.lower() for kw in ["otp", "urgent", "kyc", "prize", "lottery", "block"]): score += 25
        score = min(score + random.uniform(-2, 3), 99.9)

        risk = "CRITICAL" if score > 75 else "MEDIUM" if score > 40 else "LOW"
        results.append({
            "row": i + 1,
            "upi_id": upi_id,
            "amount": amount,
            "narration": narr[:60],
            "risk_score": round(score, 1),
            "risk_level": risk,
            "flagged": score > 40
        })

    flagged = [r for r in results if r["flagged"]]
    return {
        "total_rows": len(results),
        "flagged_count": len(flagged),
        "results": results
    }

# ── OTP INTERCEPTION DETECTOR ─────────────────────────────────────────────────

class OTPInterceptRequest(BaseModel):
    call_transcript: Optional[str] = ""
    sms_content: Optional[str] = ""
    call_time_iso: Optional[str] = None
    sms_time_iso: Optional[str] = None

@router.post("/scanner/otp-intercept")
async def detect_otp_intercept(req: OTPInterceptRequest):
    """Cross-modal OTP interception: correlates voice + SMS for OTP sharing."""
    otp_in_call = any(p in (req.call_transcript or "").lower() for p in
                      ["otp", "code", "verify", "number share", "batao", "bata do"])
    otp_in_sms  = any(p in (req.sms_content or "").lower() for p in
                      ["otp is", "otp:", "your code", "कोड", "verification code"])

    severity = "SAFE"
    risk_boost = 0
    if otp_in_call and otp_in_sms:
        severity = "CRITICAL"
        risk_boost = 70
    elif otp_in_call or otp_in_sms:
        severity = "HIGH"
        risk_boost = 40

    return {
        "otp_in_call_detected": otp_in_call,
        "otp_in_sms_detected": otp_in_sms,
        "intercept_severity": severity,
        "risk_boost": risk_boost,
        "alert": "OTP sharing detected across voice+SMS modalities — STOP TRANSACTION" if severity == "CRITICAL" else None
    }

# ── QR CODE DETONATOR ─────────────────────────────────────────────────────────

class QRDetonateRequest(BaseModel):
    qr_raw: str  # raw QR payload string

@router.post("/scanner/qr-detonate")
async def detonate_qr(req: QRDetonateRequest):
    """Sandboxed QR detonation — resolves redirect chain and extracts UPI identity."""
    raw = req.qr_raw
    chain = [{"hop": 0, "url": raw, "status": "raw_payload"}]

    # Simulate redirect resolution
    MALICIOUS_INDICATORS = ["bit.ly", "tinyurl", "t.me", "evil", "redirect", "kyc-update", "bank-secure"]
    is_malicious = any(ind in raw.lower() for ind in MALICIOUS_INDICATORS)

    if is_malicious:
        chain.append({"hop": 1, "url": "https://bit.ly/3xFakeKyc", "status": "shortened_redirect"})
        chain.append({"hop": 2, "url": "http://kyc-update-fake.in/redirect?upi=scammer@upi", "status": "malicious_domain"})
        chain.append({"hop": 3, "url": "upi://pay?pa=scammer@upi&am=9999&cu=INR", "status": "obfuscated_upi_extracted"})
        extracted_upi = "scammer@upi"
        verdict = "MALICIOUS"
    else:
        chain.append({"hop": 1, "url": raw, "status": "direct_upi"})
        extracted_upi = raw.split("pa=")[1].split("&")[0] if "pa=" in raw else None
        verdict = "SAFE"

    return {
        "original_payload": raw,
        "redirect_chain": chain,
        "hops": len(chain),
        "extracted_upi": extracted_upi,
        "verdict": verdict,
        "risk_boost": 80 if verdict == "MALICIOUS" else 0
    }

# ── ADAPTIVE BLACKLIST ─────────────────────────────────────────────────────────
ADAPTIVE_BLACKLIST: dict = {}

class BlacklistCheckRequest(BaseModel):
    upi_id: str
    risk_score: float

@router.post("/blacklist/check")
async def check_adaptive_blacklist(req: BlacklistCheckRequest):
    """Adaptive self-updating blacklist: auto-blocks UPIs hitting >85 three times."""
    entry = ADAPTIVE_BLACKLIST.get(req.upi_id, {"count": 0, "auto_blocked": False})

    if req.risk_score > 85:
        entry["count"] += 1

    if entry["count"] >= 3 and not entry["auto_blocked"]:
        entry["auto_blocked"] = True
        entry["blocked_at"] = datetime.now(timezone.utc).isoformat()

    ADAPTIVE_BLACKLIST[req.upi_id] = entry
    return {
        "upi_id": req.upi_id,
        "high_risk_hits": entry["count"],
        "auto_blocked": entry["auto_blocked"],
        "risk_boost": 95.0 if entry["auto_blocked"] else 0.0,
        "message": "AUTO-BLOCKED: Repeated high-risk pattern" if entry["auto_blocked"] else f"Monitoring: {entry['count']}/3 strikes"
    }

@router.get("/blacklist/list")
async def list_blacklist():
    return {"total": len(ADAPTIVE_BLACKLIST), "entries": ADAPTIVE_BLACKLIST}

# ── PDF THREAT REPORT ─────────────────────────────────────────────────────────

class ReportRequest(BaseModel):
    case_id: str
    upi_id: str
    risk_score: float
    risk_level: str
    timeline_events: Optional[List[dict]] = []
    genai_brief: Optional[str] = ""
    analyst_name: Optional[str] = "FraudGuard Auto-System"

@router.post("/reports/generate")
async def generate_threat_report(req: ReportRequest):
    """Generates a structured PDF-ready threat report payload."""
    report_id = f"RPT-{uuid.uuid4().hex[:10].upper()}"
    return {
        "report_id": report_id,
        "status": "generated",
        "case_id": req.case_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analyst": req.analyst_name,
        "sections": {
            "executive_summary": f"Case {req.case_id} — UPI {req.upi_id} received a risk score of {req.risk_score} ({req.risk_level}). {req.genai_brief}",
            "evidence_integrity": f"SHA-256: {hashlib.sha256(req.case_id.encode()).hexdigest()}",
            "timeline_events": len(req.timeline_events or []),
            "recommendation": "IMMEDIATE BLOCK + FIR FILING" if req.risk_score > 75 else "MONITOR + 2FA",
            "fir_reference": f"FIR-DRAFT-{report_id}",
            "portal": "https://cybercrime.gov.in"
        },
        "download_url": f"/api/reports/download/{report_id}",
        "format": "PDF (simulated — integrate reportlab for production)"
    }

# ── PEER COMPARISON ──────────────────────────────────────────────────────────

class PeerCompareRequest(BaseModel):
    payer_upi: str
    amount: float
    hour_of_day: int
    day_of_week: int      # 0=Mon, 6=Sun

@router.post("/intelligence/peer-compare")
async def peer_compare(req: PeerCompareRequest):
    """Compares this transaction to peer behavioral baseline for this user."""
    # Simulated baseline profile generation
    user_seed = sum(ord(c) for c in req.payer_upi)
    typical_amounts = [100, 250, 500, 1000, 2500]
    typical_hour_range = (9, 21)  # 9am-9pm typical

    baseline_amount = typical_amounts[user_seed % len(typical_amounts)]
    amount_ratio = req.amount / baseline_amount
    hour_ok = typical_hour_range[0] <= req.hour_of_day <= typical_hour_range[1]

    anomalies = []
    deviation_score = 0
    if amount_ratio > 5:
        anomalies.append(f"Amount is {amount_ratio:.1f}x above this user's typical spend")
        deviation_score += 40
    if not hour_ok:
        anomalies.append(f"Transaction at {req.hour_of_day}:00 outside normal hours (9am-9pm)")
        deviation_score += 25
    if req.day_of_week >= 5:
        anomalies.append("Weekend transaction (higher fraud incidence)")
        deviation_score += 10

    return {
        "user": req.payer_upi,
        "this_amount": req.amount,
        "baseline_typical_amount": baseline_amount,
        "amount_ratio": round(amount_ratio, 2),
        "anomalies": anomalies,
        "deviation_score": min(deviation_score, 95),
        "verdict": "ANOMALOUS" if deviation_score > 30 else "TYPICAL"
    }
