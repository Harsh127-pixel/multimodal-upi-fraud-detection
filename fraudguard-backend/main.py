from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.upi import router as upi_router
from app.api.transactions import router as transactions_router

app = FastAPI(title="FraudGuard Backend")

# Configure CORS
origins = [
    "http://localhost:9000",
    "http://127.0.0.1:9000",
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

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
