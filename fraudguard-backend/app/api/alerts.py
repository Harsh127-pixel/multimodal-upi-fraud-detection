from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as redis
import os
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

@router.websocket("/ws/alerts/{user_id}")
async def websocket_alerts(websocket: WebSocket, user_id: str):
    await websocket.accept()
    
    # Establish Redis connection for this websocket
    r = redis.from_url(REDIS_URL, decode_responses=True)
    pubsub = r.pubsub()
    channel = f"alerts:{user_id}"
    
    try:
        await pubsub.subscribe(channel)
        logger.info(f"User {user_id} connected to alerts WebSocket")
        
        while True:
            # Check for messages in the pubsub channel
            # Wait for message with a timeout to allow checking for disconnect
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            
            if message:
                try:
                    # Forward the JSON message string to the WebSocket client
                    await websocket.send_text(message['data'])
                except Exception as send_err:
                    logger.error(f"Error sending message to client {user_id}: {str(send_err)}")
                    break
            
            # Periodically yield back to the event loop
            await asyncio.sleep(0.01)
            
    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected from alerts WebSocket")
    except Exception as e:
        logger.error(f"Unexpected WebSocket error for user {user_id}: {str(e)}")
    finally:
        # Cleanup
        try:
            await pubsub.unsubscribe(channel)
            await r.close()
        except:
            pass
        logger.info(f"Cleaned up resources for user {user_id}")
