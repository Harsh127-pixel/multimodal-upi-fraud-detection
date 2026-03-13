from fastapi import FastAPI, File, UploadFile, Form, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import torch
import torch.nn as nn
from typing import List, Optional
import json
import uvicorn
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import firebase_admin
from firebase_admin import credentials, firestore

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
        'databaseURL': os.getenv("FIREBASE_DATABASE_URL")
    })
    db = firestore.client()
else:
    print("Warning: Firebase service account path not found or not provided.")
    db = None

app = FastAPI(title="SafeUPI Multimodal Fraud Detection API")

# Placeholder for PyTorch Model
class FraudDetectionModel(nn.Module):
    def __init__(self, input_dim=512, hidden_dim=256, output_dim=1):
        super(FraudDetectionModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return self.sigmoid(x)

# Initialize model (placeholder weights)
model = FraudDetectionModel()
model.eval()

class TransactionData(BaseModel):
    upi_id: str
    amount: float
    message: str
    timestamp: str

class RiskResult(BaseModel):
    risk_score: float
    risk_level: str
    flags: List[str]

@app.get("/")
def read_root():
    return {"message": "SafeUPI API is online", "status": "active"}

@app.post("/analyze/transaction", response_model=RiskResult)
async def analyze_transaction(data: TransactionData):
    # This is where NLP and Risk Fusion logic would go
    # For now, let's simulate a risk score using the placeholder model
    # Convert some features to a tensor
    input_tensor = torch.randn(1, 512) # Dummy features
    with torch.no_grad():
        prediction = model(input_tensor).item()
    
    risk_level = "High" if prediction > 0.7 else "Medium" if prediction > 0.3 else "Low"
    
    return {
        "risk_score": round(prediction * 100, 2),
        "risk_level": risk_level,
        "flags": ["Message pattern check" if "urgent" in data.message.lower() else "Standard check"]
    }

from voice_detection.predict import assess_voice_authenticity
from voice_detection.utils import detect_scam_keywords, build_alert

@app.post("/analyze/voice")
async def analyze_voice(
    file: UploadFile = File(...),
    transaction_id: str = Form("TXN_UNKNOWN"),
    unusual_transaction: bool = Form(False),
    new_device: bool = Form(False)
):
    # 1. Upload to Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(file.file, resource_type="auto", folder="voice_samples")
        file_url = upload_result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")

    # 2. Process audio and detect voice authenticity using our trained model
    try:
        # Seek to beginning of file stream (since cloudinary consumed it)
        await file.seek(0)
        audio_bytes = await file.read()
        
        # Run inference using the prediction pipeline
        assessment = assess_voice_authenticity(audio_bytes)
        
        if not assessment.get("success"):
            raise HTTPException(status_code=500, detail=assessment.get("error", "Unknown error during audio processing."))
            
        real_score = assessment["is_real_probability"]
        is_impersonation = real_score < 0.50
        fake_confidence = assessment["is_fake_probability"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice analysis failed: {str(e)}")

    # 3. Fraud Decision Engine
    fraud_score = 0
    
    if real_score < 0.5:
        fraud_score += 40
        
    if unusual_transaction:
        fraud_score += 30
        
    if new_device:
        fraud_score += 20
        
    fraud_risk = "HIGH" if fraud_score > 60 else "MEDIUM" if fraud_score > 30 else "LOW"
    final_action = "BLOCK_TRANSACTION" if fraud_score > 60 else "ALLOW"

    # 4. Log Fraud Results to Firebase Firestore
    if db:
        try:
            doc_ref = db.collection(u'fraud_analysis').document()
            doc_ref.set({
                u'transaction_id': transaction_id,
                u'voice_authenticity_score': round(real_score, 4),
                u'fraud_risk': fraud_risk,
                u'action': final_action,
                u'timestamp': firestore.SERVER_TIMESTAMP,
                # Additional metadata for debugging 
                u'file_url': file_url,
                u'fraud_score_raw': fraud_score
            })
        except Exception as e:
            print(f"Firebase logging failed: {str(e)}")

    # 5. Return the integrated fraud assessment
    return {
        "transaction_id": transaction_id,
        "filename": file.filename,
        "file_url": file_url,
        "is_impersonation": is_impersonation,
        "confidence": fake_confidence,
        "voice_authenticity_score": real_score,
        "fraud_score": fraud_score,
        "fraud_risk": fraud_risk,
        "action": final_action,
        "message": "Voice analysis and fraud assessment completed successfully"
    }

@app.websocket("/ws/live-scam-detection")
async def live_scam_detection(websocket: WebSocket):
    """
    WebSocket endpoint for real-time scam detection during a live phone call.

    Flow:
      Client sends JSON per audio chunk:
        {
          "audio_b64": "<base64-encoded audio bytes>",
          "transcript": "share your OTP immediately"
        }

      Server responds with real-time alert:
        {
          "is_scam": true,
          "alert_messages": ["⚠️ Caller voice appears synthetic", "⚠️ Suspicious phrases heard: otp, immediately"],
          "voice_authenticity_score": 0.21,
          "keyword_risk_level": "HIGH",
          "matched_keywords": ["otp", "immediately"]
        }
    """
    await websocket.accept()
    print("[WS] Live scam detection session started.")

    try:
        while True:
            # 1. Receive the next audio chunk from client
            raw_data = await websocket.receive_text()
            payload = json.loads(raw_data)

            audio_b64 = payload.get("audio_b64", "")
            transcript = payload.get("transcript", "")

            # 2. Voice deepfake detection on the audio chunk
            voice_score = 0.5  # Default neutral if no audio provided
            if audio_b64:
                import base64
                audio_bytes = base64.b64decode(audio_b64)
                assessment = assess_voice_authenticity(audio_bytes)
                if assessment.get("success"):
                    voice_score = assessment["is_real_probability"]

            # 3. Scam keyword detection on the transcript
            keyword_result = detect_scam_keywords(transcript)

            # 4. Build the final alert
            alert = build_alert(voice_score, keyword_result)

            # 5. Send back the real-time alert to the client
            await websocket.send_text(json.dumps(alert))

    except WebSocketDisconnect:
        print("[WS] Client disconnected from live scam detection session.")
    except Exception as e:
        print(f"[WS] Error during live scam detection: {e}")
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
