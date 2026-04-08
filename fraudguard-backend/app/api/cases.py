"""
FraudGuard Case Management System
Analyst case workflow: Open → Investigating → Resolved
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/cases", tags=["Case Management"])

# In-memory case store (prototype)
CASE_STORE: dict = {}

class CreateCaseRequest(BaseModel):
    tx_id: str
    upi_id: str
    risk_score: float
    risk_level: str
    summary: str
    assigned_to: Optional[str] = "Unassigned"

class UpdateCaseRequest(BaseModel):
    status: Optional[str] = None        # open | investigating | resolved | false_positive
    notes: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None

@router.post("/create")
async def create_case(req: CreateCaseRequest):
    case_id = f"FG-{uuid.uuid4().hex[:8].upper()}"
    case = {
        "case_id": case_id,
        "tx_id": req.tx_id,
        "upi_id": req.upi_id,
        "risk_score": req.risk_score,
        "risk_level": req.risk_level,
        "summary": req.summary,
        "status": "open",
        "assigned_to": req.assigned_to,
        "notes": [],
        "resolution": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    CASE_STORE[case_id] = case
    return {"case_id": case_id, "status": "open", "message": "Case created successfully"}

@router.get("/list")
async def list_cases():
    return {
        "total": len(CASE_STORE),
        "cases": list(CASE_STORE.values())
    }

@router.get("/{case_id}")
async def get_case(case_id: str):
    case = CASE_STORE.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return case

@router.patch("/{case_id}")
async def update_case(case_id: str, req: UpdateCaseRequest):
    case = CASE_STORE.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    if req.status:
        case["status"] = req.status
    if req.notes:
        case["notes"].append({
            "text": req.notes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    if req.assigned_to:
        case["assigned_to"] = req.assigned_to
    if req.resolution:
        case["resolution"] = req.resolution

    case["updated_at"] = datetime.now(timezone.utc).isoformat()
    return {"case_id": case_id, "updated": True, "case": case}

@router.get("/stats/summary")
async def case_stats():
    cases = list(CASE_STORE.values())
    return {
        "total": len(cases),
        "open": sum(1 for c in cases if c["status"] == "open"),
        "investigating": sum(1 for c in cases if c["status"] == "investigating"),
        "resolved": sum(1 for c in cases if c["status"] == "resolved"),
        "false_positive": sum(1 for c in cases if c["status"] == "false_positive"),
        "critical": sum(1 for c in cases if c["risk_level"] == "CRITICAL"),
    }
