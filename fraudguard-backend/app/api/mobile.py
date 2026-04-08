from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import random

router = APIRouter(tags=["Mobile Security"])

class DeviceTelemetry(BaseModel):
    device_id: str
    is_rooted: bool
    active_overlay_apps: List[str]
    sim_serial: str
    location: dict # {"lat": float, "lng": float}
    ips_connected: List[str]
    wifi_security: str = "WPA2"
    active_keyboards: List[str] = ["com.google.android.inputmethod.latin"]
    accessibility_services_enabled: bool = False

class MobileRiskResponse(BaseModel):
    overall_health: str # "SECURE", "COMPROMISED", "WARNED"
    threats: List[str]
    score: float
    recommendations: List[str]

@router.post("/telemetry", response_model=MobileRiskResponse)
async def analyze_telemetry(data: DeviceTelemetry):
    threats = []
    score = 100.0
    
    # 1. Overlay Detection
    high_risk_overlays = ["AnyDesk", "TeamViewer", "QuickSupport", "ApowerMirror"]
    for app in data.active_overlay_apps:
        if app in high_risk_overlays:
            threats.append(f"Remote access app detected: {app}")
            score -= 40
            
    # 2. Root/Jailbreak Integrity
    if data.is_rooted:
        threats.append("Device is Rooted/Jailbroken (OS Integrity Compromised)")
        score -= 30
        
    # 3. SIM-Swap (Simulated check)
    if "SIM_SERIAL_OLD" in data.sim_serial:
        threats.append("SIM Card Serial mismatch - Potential SIM Swap detected")
        score -= 50

    # 4. Geofence (Simulated)
    # Target: Flag if lat/lng is significantly away from India (mock)
    if not (8.0 < data.location.get('lat', 0) < 37.0):
         threats.append("Anomalous Location: Transaction originating from outside registered geofence")
         score -= 20

    # 5. Rogue WiFi / Man-in-the-Middle
    if data.wifi_security in ["OPEN", "WEP"]:
         threats.append(f"Insecure Network Connection ({data.wifi_security}). Man-in-the-Middle risk.")
         score -= 25

    # 6. Keylogger Monitor
    trusted_keyboards = ["com.google.android.inputmethod.latin", "com.apple.keyboards", "com.samsung.android.honeyboard"]
    for kb in data.active_keyboards:
        if kb not in trusted_keyboards:
             threats.append(f"Untrusted 3rd-party Keyboard active: {kb}")
             score -= 30

    # 7. Accessibility Abuse (Intent Guard)
    if data.accessibility_services_enabled:
         threats.append("Accessibility Services Enabled: Potential Auto-clicker malware detected")
         score -= 35

    recommendations = []
    if score < 70:
        recommendations.append("Uninstall remote desktop applications.")
        recommendations.append("Revert device to factory OS (Disable Root).")
    
    health = "SECURE" if score > 80 else "WARNED" if score > 50 else "COMPROMISED"
    
    return {
        "overall_health": health,
        "threats": threats,
        "score": max(0, score),
        "recommendations": recommendations
    }

class QRValidationRequest(BaseModel):
    qr_data: str
    scanner_location: Optional[dict]

@router.post("/qr/verify")
async def verify_qr(req: QRValidationRequest):
    # Simulated QR check
    if "upi://" not in req.qr_data:
        return {"status": "MALICIOUS", "reason": "Not a valid UPI deep link"}
    
    if "redirect" in req.qr_data or "http" in req.qr_data:
        return {"status": "MALICIOUS", "reason": "QR contains malicious redirection payload"}
    
    return {"status": "SECURE", "merchant": "Simulated Merchant", "risk_score": 0.05}

class SMSLinkRequest(BaseModel):
    url: str
    sms_text: str

@router.post("/sms/sandbox")
async def sandbox_link(req: SMSLinkRequest):
    # Simulated URL Sandbox
    malicious_keywords = ["bank-update", "verif-id", "kyc-portal", "gift-card"]
    is_malicious = any(kw in req.url.lower() for kw in malicious_keywords)
    
    return {
        "status": "DANGER" if is_malicious else "SAFE",
        "threat_type": "Phish-Kit" if is_malicious else None,
        "final_url": req.url,
        "screenshot_url": "https://simulated-sandbox.io/capture/123"
    }

class ClipboardRequest(BaseModel):
    pasted_text: str

@router.post("/clipboard/scan")
async def scan_clipboard(req: ClipboardRequest):
    # Simulated Clipboard Hijacking detection
    scammer_upis = ["fraudster@upi", "scammer123@okaxis", "fake_charity@ybl"]
    is_poisoned = any(upi in req.pasted_text for upi in scammer_upis)
    
    return {
        "status": "POISONED" if is_poisoned else "CLEAN",
        "intercepted_match": "fraudster@upi" if is_poisoned else None,
        "action_taken": "BLOCKED" if is_poisoned else "ALLOWED"
    }

class CallInterceptRequest(BaseModel):
    caller_id: str
    caller_name: Optional[str]

@router.post("/call/intercept")
async def intercept_call(req: CallInterceptRequest):
    # Simulated Global Blacklist checking & Deepfake probability lookup
    vishing_numbers = ["+919876543210", "+18005559999"]
    
    if req.caller_id in vishing_numbers:
        return {
            "action": "DROP_CALL",
            "reason": "Known Vishing Syndicate",
            "deepfake_probability": 0.92
        }
        
    return {
        "action": "ALLOW",
        "reason": "Clear",
        "deepfake_probability": 0.05
    }
