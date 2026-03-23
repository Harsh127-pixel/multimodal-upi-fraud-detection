from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
import shutil
from typing import Any
from celery.result import AsyncResult
from app.workers.celery_app import celery_app

router = APIRouter()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

MAX_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    # Validate MIME type
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only audio files are allowed.")
    
    # Save temporarily
    task_id = str(uuid.uuid4())
    filename = f"{task_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Check size (FastAPI doesn't do this automatically for spooling)
    # We can read size from file.file.tell() after seeking but it's easier to just read and check
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10MB).")
    
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Queue task
    celery_app.send_task("app.workers.audio_task.analyze_audio", args=[file_path], task_id=task_id)
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Audio analysis started. Poll /api/audio/result/{task_id} for results."
    }

@router.get("/result/{task_id}")
async def get_audio_result(task_id: str):
    res = AsyncResult(task_id, app=celery_app)
    
    if res.state == "SUCCESS":
        result = res.get()
        if isinstance(result, dict) and "error" in result:
             return {"status": "failed", "error": result["error"]}
        return {"status": "complete", **result}
    elif res.state == "FAILURE":
        return {"status": "failed", "error": str(res.result)}
    else:
        return {"status": "processing"}
