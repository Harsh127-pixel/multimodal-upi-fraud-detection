# 🛡️ Multimodal UPI Fraud Detection

**Multimodal UPI Fraud Detection** is an advanced AI-powered system designed to analyze and flag potential fraud in UPI transactions by combining data from multiple input modalities: **voice recordings** (deepfake/impersonation), **text messages** (phishing links/scam language), and **transaction metadata** (risk scoring).

---

## 💡 Project Overview

With the rise of UPI usage, fraudsters employ sophisticated social engineering tactics—ranging from phishing texts to AI-generated voice clones. This project acts as a safety layer by using a multimodal approach:

1. **Voice Impersonation Detection**: Uses a PyTorch ResNet-based model to classify audio samples as authentic or fabricated.
2. **NLP Text Scan**: Uses Transformer models to analyze associated text messages for scam triggers.
3. **Risk Fusion Engine**: Combines the output of the voice and text models with transaction metadata to output a final High/Medium/Low risk score.

---

## 🏗️ System Architecture

```text
multimodal-upi-fraud-detection/
├── dataset/                     # Raw training data (gitignored — add locally)
│   ├── LA.zip                   # ASVspoof2019 Logical Access dataset
│   └── PA.zip                   # ASVspoof2019 Physical Access dataset
├── ml_models/                   # PyTorch Models & Risk Engine
│   ├── voice_detection/         # Audio analysis models
│   ├── impersonation_nlp/       # Transformer-based NLP text models
│   └── risk_engine/             # Final risk calculation logic
├── backend/                     # ML API & Logic (FastAPI)
│   ├── src/                     # Core API implementation
│   ├── data/                    # Storage for input Datasets
│   ├── notebooks/               # Jupyter research notebooks
│   ├── app/                     # Streamlit demo
│   └── requirements.txt         # Backend Python dependencies
├── frontend/                    # Vue 3 Dashboard
│   └── src/                     # Components and styling
├── docs/                        # Project research and reports
├── .gitignore                   # Exclusions for git
└── README.md                    # Main Project Documentation
```

---

## 🛠️ Tech Stack

**Frontend:**

- **Vue 3** + **Vite** (Composition API)
- Vanilla CSS (Glassmorphism design system)

**Backend & API:**

- **FastAPI** (High-performance API routing)
- **Uvicorn** (ASGI Server)
- **Streamlit** (Alternative prototype UI)

**Machine Learning & Data:**

- **PyTorch** & **Transformers** (Neural Network Architecture)
- **Librosa** & **Soundfile** (Audio signal processing)
- **Scikit-learn** & **Pandas** (Data manipulation)

**Database & Cloud:**

- **Firebase Firestore** (Metadata and logging)
- **Cloudinary** (Secure audio storage)

---

## 🚀 Setup Instructions

### 1. Backend Setup

Navigate into the backend directory and install the required dependencies:

```bash
cd backend
pip install -r requirements.txt
```

#### Environment Variables

Create a `.env` file inside the `backend/` directory by copying `.env.example`. Add your Cloudinary keys and Firebase Service Account key:

```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_key
CLOUDINARY_API_SECRET=your_secret
FIREBASE_SERVICE_ACCOUNT_PATH=serviceAccountKey.json
```

Start the API server:

```bash
python src/api/main.py
```

_API Docs available at: `http://localhost:8000/docs`_

### 2. Frontend Setup

Navigate into the frontend directory:

```bash
cd frontend
npm install
npm run dev
```

_Dashboard available at `http://localhost:5173`_

---

## 🌐 API Endpoints

- `GET /` - Health check status.
- `POST /analyze/transaction` - Accepts JSON containing `upi_id`, `amount`, and `message` to calculate a risk severity score.
- `POST /analyze/voice` - Accepts a `.wav`/`.mp3` multipart upload. Uploads to Cloudinary, processes audio for impersonation, and logs the result to Firebase.

---

## 🔮 Future Work

- Integration with live SMS APIs for real-time text interception.
- Expanding the UPI risk fusion model to analyze historical transaction velocity.
- Adding a user feedback loop to the dashboard to correct False Positives and further train the models.
- Deploying the backend via Docker containers to AWS/GCP.
