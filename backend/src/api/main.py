from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import torch
import torch.nn as nn
from typing import List, Optional
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

@app.post("/analyze/voice")
async def analyze_voice(file: UploadFile = File(...)):
    # 1. Upload to Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(file.file, resource_type="auto", folder="voice_samples")
        file_url = upload_result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")

    # 2. Placeholder for audio processing and voice detection logic
    # (In a real app, you'd process the file_url or the local file here)
    is_impersonation = False
    confidence = 0.92

    # 3. Log result to Firebase Firestore
    if db:
        try:
            doc_ref = db.collection(u'voice_detections').document()
            doc_ref.set({
                u'filename': file.filename,
                u'file_url': file_url,
                u'is_impersonation': is_impersonation,
                u'confidence': confidence,
                u'timestamp': firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            print(f"Firebase logging failed: {str(e)}")

    return {
        "filename": file.filename,
        "file_url": file_url,
        "is_impersonation": is_impersonation,
        "confidence": confidence,
        "message": "Voice analysis completed and logged successfully"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
