import requests
import json

url = "http://localhost:8000/api/transactions/score"
payload = {
    "upi_id": "scammer@fake",
    "amount": 20000,
    "device_id": "unknown",
    "timestamp": "2025-01-15T02:00:00",
    "payer_upi_id": "me@upi",
    "payer_device_id": "my-phone",
    "payer_account_age_days": 500,
    "is_post_call": True,
    "user_avg_amount": 300,
    "user_tx_count": 50
}

response = requests.post(url, json=payload)
print(f"Status Code: {response.status_code}")
print(f"Response Body: {json.dumps(response.json(), indent=2)}")
