"""
FraudGuard Alert WebSocket
Replaced Redis pubsub with a lightweight in-memory broadcast to prevent
the async event loop from blocking when Redis is unavailable.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import logging
import json
from datetime import datetime, timezone

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory alert queue (per user_id)
ALERT_QUEUES: dict[str, list] = {}

def push_alert(user_id: str, alert: dict):
    """Push an alert to a connected user's queue (called by other endpoints)."""
    if user_id not in ALERT_QUEUES:
        ALERT_QUEUES[user_id] = []
    ALERT_QUEUES[user_id].append(alert)

@router.websocket("/ws/alerts/{user_id}")
async def websocket_alerts(websocket: WebSocket, user_id: str):
    logger.info(f"WS connection for user: {user_id}")
    await websocket.accept()
    ALERT_QUEUES.setdefault(user_id, [])

    # Send a welcome ping immediately
    await websocket.send_text(json.dumps({
        "type": "connected",
        "message": "FraudGuard Alert Stream Active",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }))

    try:
        while True:
            # Drain any queued alerts
            queue = ALERT_QUEUES.get(user_id, [])
            while queue:
                alert = queue.pop(0)
                await websocket.send_text(json.dumps(alert))

            # Yield back to event loop — no blocking Redis calls
            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected from alerts WebSocket")
    except Exception as e:
        logger.warning(f"Alert WS error for {user_id}: {e}")
    finally:
        ALERT_QUEUES.pop(user_id, None)
        logger.info(f"Cleaned up alert stream for user {user_id}")
