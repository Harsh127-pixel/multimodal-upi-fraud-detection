from fastapi import FastAPI, File, UploadFile, Form, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List
import json
import os
import base64
import sys
import uvicorn
from dotenv import load_dotenv
import torch
import torch.nn as nn

# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cloudinary
import cloudinary.uploader

import firebase_admin
from firebase_admin import credentials, firestore

# Import local modules
from nlp_detection.impersonation_detector import detect_impersonation
from voice_detection.predict import assess_voice_authenticity
from voice_detection.utils import detect_scam_keywords, build_alert


class TranscriptRequest(BaseModel):
    transcript: str


# Load environment variables
load_dotenv()


# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


# Firebase Configuration
firebase_cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

if firebase_cred_path and os.path.exists(firebase_cred_path):
    cred = credentials.Certificate(firebase_cred_path)
    firebase_admin.initialize_app(cred, {
        "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
    })
    db = firestore.client()
else:
    print("Warning: Firebase service account path not found.")
    db = None


app = FastAPI(title="SafeUPI Multimodal Fraud Detection API")


# -----------------------------
# Dummy PyTorch Fraud Model
# -----------------------------
class FraudDetectionModel(nn.Module):

    def __init__(self, input_dim=512, hidden_dim=256, output_dim=1):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return self.sigmoid(x)


model = FraudDetectionModel()
model.eval()


# -----------------------------
# Request Models
# -----------------------------
class TransactionData(BaseModel):
    upi_id: str
    amount: float
    message: str
    timestamp: str


class RiskResult(BaseModel):
    risk_score: float
    risk_level: str
    flags: List[str]


# -----------------------------
# Root API
# -----------------------------
@app.get("/")
def read_root():
    return {
        "message": "SafeUPI API is online",
        "status": "active"
    }


# -----------------------------
# Transaction Risk Analysis
# -----------------------------
@app.post("/analyze/transaction", response_model=RiskResult)
async def analyze_transaction(data: TransactionData):

    input_tensor = torch.randn(1, 512)

    with torch.no_grad():
        prediction = model(input_tensor).item()

    risk_level = (
        "High" if prediction > 0.7
        else "Medium" if prediction > 0.3
        else "Low"
    )

    flags = []

    if "urgent" in data.message.lower():
        flags.append("Message pattern check")
    else:
        flags.append("Standard check")

    return {
        "risk_score": round(prediction * 100, 2),
        "risk_level": risk_level,
        "flags": flags
    }


# -----------------------------
# Voice Fraud Analysis
# -----------------------------
@app.post("/analyze/voice")
async def analyze_voice(
    file: UploadFile = File(...),
    transaction_id: str = Form("TXN_UNKNOWN"),
    unusual_transaction: bool = Form(False),
    new_device: bool = Form(False)
):

    # Upload to Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(
            file.file,
            resource_type="auto",
            folder="voice_samples"
        )

        file_url = upload_result.get("secure_url")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cloudinary upload failed: {str(e)}"
        )

    # Voice authenticity detection
    try:

        await file.seek(0)
        audio_bytes = await file.read()

        assessment = assess_voice_authenticity(audio_bytes)

        if not assessment.get("success", True):
            raise HTTPException(
                status_code=500,
                detail=assessment.get("error")
            )

        real_score = assessment.get("is_real_probability", 0.5)
        fake_confidence = assessment.get("is_fake_probability", 1 - real_score)

        is_impersonation = real_score < 0.5

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Voice analysis failed: {str(e)}"
        )

    # Fraud scoring logic
    fraud_score = 0

    if real_score < 0.5:
        fraud_score += 40

    if unusual_transaction:
        fraud_score += 30

    if new_device:
        fraud_score += 20

    fraud_risk = (
        "HIGH" if fraud_score > 60
        else "MEDIUM" if fraud_score > 30
        else "LOW"
    )

    final_action = (
        "BLOCK_TRANSACTION"
        if fraud_score > 60
        else "ALLOW"
    )

    # Save results to Firestore
    if db:
        try:
            db.collection("fraud_analysis").add({
                "transaction_id": transaction_id,
                "voice_authenticity_score": real_score,
                "fraud_risk": fraud_risk,
                "action": final_action,
                "file_url": file_url,
                "fraud_score": fraud_score,
                "timestamp": firestore.SERVER_TIMESTAMP
            })

        except Exception as e:
            print("Firebase error:", e)

    return {
        "transaction_id": transaction_id,
        "file_url": file_url,
        "voice_authenticity_score": real_score,
        "confidence": fake_confidence,
        "is_impersonation": is_impersonation,
        "fraud_score": fraud_score,
        "fraud_risk": fraud_risk,
        "action": final_action
    }


# -----------------------------
# WebSocket Live Scam Detection
# -----------------------------
@app.websocket("/ws/live-scam-detection")
async def live_scam_detection(websocket: WebSocket):

    await websocket.accept()
    print("[WS] Live scam detection started")

    try:
        while True:

            raw_data = await websocket.receive_text()
            payload = json.loads(raw_data)

            audio_b64 = payload.get("audio_b64", "")
            transcript = payload.get("transcript", "")

            voice_score = 0.5

            if audio_b64:
                try:
                    audio_bytes = base64.b64decode(audio_b64)
                    assessment = assess_voice_authenticity(audio_bytes)

                    if assessment.get("success", True):
                        voice_score = assessment.get("is_real_probability", 0.5)

                except Exception as e:
                    print("[WS] audio error:", e)

            keyword_result = detect_scam_keywords(transcript)

            alert = build_alert(voice_score, keyword_result)

            await websocket.send_text(json.dumps(alert))

    except WebSocketDisconnect:
        print("[WS] Client disconnected")

    except Exception as e:
        print("[WS] error:", e)
        await websocket.close()


# -----------------------------
# NLP Impersonation Detection
# -----------------------------
@app.post("/detect-impersonation")
def detect_scam(data: TranscriptRequest):

    result = detect_impersonation(data.transcript)

    return result


# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    uvicorn.run("backend.src.api.main:app", host="0.0.0.0", port=8000, reload=True)