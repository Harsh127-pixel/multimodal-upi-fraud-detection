from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.upi import router as upi_router
from app.api.transactions import router as transactions_router
from app.api.alerts import router as alerts_router
from app.api.sms import router as sms_router
from app.api.calls import router as calls_router
from app.api.multimodal import router as multi_router
from app.api.audio import router as audio_router
from app.api.reports import router as reports_router
from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.advanced import router as advanced_router
from app.api.mobile import router as mobile_router
from app.api.graph import router as graph_router
from app.api.community import router as community_router
from app.api.legal import router as legal_router
from app.api.genai import router as genai_router
from app.api.intelligence import router as intelligence_router
from app.api.cases import router as cases_router
from app.api.soc import router as soc_router
from app.api.playbook import router as playbook_router
from app.api.scanner import router as scanner_router

app = FastAPI(title="FraudGuard Backend")

# Configure CORS
origins = [
    "http://localhost:9000",
    "http://127.0.0.1:9000",
    "http://localhost:9001",
    "http://127.0.0.1:9001",
    "http://localhost:9002",
    "http://127.0.0.1:9002",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "https://multimodal-upi-fraud-detection.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upi_router, prefix="/api/upi", tags=["upi"])
app.include_router(transactions_router, prefix="/api/transactions", tags=["transactions"])
app.include_router(alerts_router, tags=["alerts"])
app.include_router(sms_router, prefix="/api/sms", tags=["sms"])
app.include_router(calls_router, prefix="/api/calls", tags=["calls"])
app.include_router(multi_router, prefix="/api/multi", tags=["multi"])
app.include_router(audio_router, prefix="/api/audio", tags=["audio"])
app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(advanced_router, prefix="/api/advanced", tags=["advanced"])
app.include_router(mobile_router, prefix="/api/mobile", tags=["mobile"])
app.include_router(graph_router, prefix="/api", tags=["graph"])
app.include_router(community_router, prefix="/api", tags=["community"])
app.include_router(legal_router, prefix="/api", tags=["legal"])
app.include_router(genai_router, prefix="/api", tags=["genai"])
app.include_router(intelligence_router, prefix="/api", tags=["intelligence"])
app.include_router(cases_router, prefix="/api", tags=["cases"])
app.include_router(soc_router, prefix="/api", tags=["soc"])
app.include_router(playbook_router, prefix="/api", tags=["playbook"])
app.include_router(scanner_router, prefix="/api", tags=["scanner"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
