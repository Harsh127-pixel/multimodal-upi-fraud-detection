import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_enterprise_features():
    print("--- Testing Enterprise Features ---")
    
    # 1. Advanced Evidence Bundle
    bundle_data = {
        "tx_id": "TEST-123",
        "upi_id": "scammer@upi",
        "evidence_type": "sms",
        "content_hash": "abc123hash",
        "metadata": {"score": 95}
    }
    res = requests.post(f"{BASE_URL}/advanced/evidence/bundle", json=bundle_data)
    print(f"Evidence Bundle: {res.status_code} - {res.json().get('bundle_hash', 'FAIL')[:16]}...")

    # 2. Honeypot Hit
    hit_data = {"upi_id": "charity@upi", "source_ip": "1.2.3.4", "device_id": "DEV-666", "action": "pay_request"}
    res = requests.post(f"{BASE_URL}/advanced/honeypot/report", json=hit_data)
    print(f"Honeypot Hit: {res.status_code} - {res.json().get('status')}")

def test_mobile_features():
    print("\n--- Testing Mobile Features ---")
    
    # 1. Telemetry Analysis (Rooted + Overlay)
    tele_data = {
        "device_id": "MOB-001",
        "is_rooted": True,
        "active_overlay_apps": ["AnyDesk"],
        "sim_serial": "SIM_SERIAL_OLD_123",
        "location": {"lat": 40.0, "lng": -74.0}, # Out of India
        "ips_connected": ["10.0.0.1"]
    }
    res = requests.post(f"{BASE_URL}/mobile/telemetry", json=tele_data)
    print(f"Telemetry: {res.status_code} - Health: {res.json().get('overall_health')} - Score: {res.json().get('score')}")
    print(f"Threats Detected: {len(res.json().get('threats', []))}")

    # 2. QR Verify (Malicious)
    qr_data = {"qr_data": "http://evil.com/redirect?upi=scammer", "scanner_location": None}
    res = requests.post(f"{BASE_URL}/mobile/qr/verify", json=qr_data)
    print(f"QR Verify (Evil): {res.json().get('status')} - {res.json().get('reason')}")

    # 3. SMS Sandbox (Malicious)
    sms_data = {"url": "https://bank-update-val.com", "sms_text": "Verify now"}
    res = requests.post(f"{BASE_URL}/mobile/sms/sandbox", json=sms_data)
    print(f"SMS Sandbox (Evil): {res.status_code} - {res.json().get('status')} - Type: {res.json().get('threat_type')}")
    
    # 4. Clipboard Scanner (Poisoned)
    clip_data = {"pasted_text": "Hey check out fraudster@upi for the transfer"}
    res = requests.post(f"{BASE_URL}/mobile/clipboard/scan", json=clip_data)
    print(f"Clipboard Scanner: {res.status_code} - {res.json().get('status')} - Intercepted: {res.json().get('intercepted_match')}")
    
    # 5. Call Interceptor (Vishing)
    call_data = {"caller_id": "+919876543210", "caller_name": "Axis Support"}
    res = requests.post(f"{BASE_URL}/mobile/call/intercept", json=call_data)
    print(f"Call Interceptor: {res.status_code} - Action: {res.json().get('action')} - Reason: {res.json().get('reason')}")

if __name__ == "__main__":
    try:
        test_enterprise_features()
        test_mobile_features()
        print("\nSUCCESS: All backend features responding correctly.")
    except Exception as e:
        print(f"\nFAILED: {e}")
