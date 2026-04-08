"""
FraudGuard Automated Incident Playbook Executor
Executes step-by-step response runbooks when CRITICAL threats are detected.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import asyncio, uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/playbook", tags=["Playbook"])

# In-memory playbook run store
PLAYBOOK_RUNS: dict = {}

PLAYBOOK_STEPS = [
    {"step": 1, "name": "Freeze Suspected Account",    "icon": "lock",            "detail": "Sending account freeze signal to NPCI gateway..."},
    {"step": 2, "name": "Alert Victim via SMS",         "icon": "sms",             "detail": "Dispatching high-priority SMS alert to registered mobile..."},
    {"step": 3, "name": "Notify Bank Fraud Desk",       "icon": "account_balance", "detail": "Posting incident report to bank's Fraud Management Cell..."},
    {"step": 4, "name": "Blacklist Threat Actor",       "icon": "block",           "detail": "Adding UPI ID + device fingerprint to global blacklist..."},
    {"step": 5, "name": "Create Priority Case",         "icon": "folder_special",  "detail": "Routing to Tier-1 analyst queue with CRITICAL priority tag..."},
    {"step": 6, "name": "File Auto-FIR Draft",          "icon": "gavel",           "detail": "Preparing pre-filled FIR payload for 1930 cybercrime portal..."},
]

class PlaybookRequest(BaseModel):
    tx_id: str
    upi_id: str
    risk_score: float
    triggered_by: Optional[str] = "Auto-System"

@router.post("/execute")
async def execute_playbook(req: PlaybookRequest):
    """Kicks off the automated CRITICAL incident playbook."""
    run_id = f"PB-{uuid.uuid4().hex[:8].upper()}"
    PLAYBOOK_RUNS[run_id] = {
        "run_id": run_id,
        "tx_id": req.tx_id,
        "upi_id": req.upi_id,
        "risk_score": req.risk_score,
        "triggered_by": req.triggered_by,
        "status": "running",
        "steps_completed": 0,
        "total_steps": len(PLAYBOOK_STEPS),
        "steps": [],
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    return {"run_id": run_id, "status": "running", "total_steps": len(PLAYBOOK_STEPS)}

@router.get("/status/{run_id}")
async def get_playbook_status(run_id: str):
    """Polls the execution state of a running playbook."""
    run = PLAYBOOK_RUNS.get(run_id)
    if not run:
        return {"run_id": run_id, "status": "not_found"}

    completed = run["steps_completed"]

    if completed < len(PLAYBOOK_STEPS):
        next_step = PLAYBOOK_STEPS[completed]
        run["steps"].append({
            **next_step,
            "status": "done",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        run["steps_completed"] += 1

        if run["steps_completed"] >= len(PLAYBOOK_STEPS):
            run["status"] = "complete"
            run["completed_at"] = datetime.now(timezone.utc).isoformat()

    return run
