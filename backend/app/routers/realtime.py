"""Real-time audio identification via WebSocket."""

import asyncio
import base64
import io
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter()


class RealtimeSession:
    """Manages a real-time audio identification session."""
    
    def __init__(self, websocket: WebSocket, audio_classifier):
        self.websocket = websocket
        self.audio_classifier = audio_classifier
        self.is_active = True
        self.detections: List[Dict[str, Any]] = []
        # Store full species info keyed by species_id for better tracking
        self.detection_history: Dict[int, Dict[str, Any]] = {}  # species_id -> full info with best confidence
    
    async def process_audio_chunk(self, audio_data: bytes) -> List[Dict[str, Any]]:
        """Process an audio chunk and return detections."""
        audio_bytes = io.BytesIO(audio_data)
        
        # Run prediction (this is sync, but we'll run it in executor)
        loop = asyncio.get_event_loop()
        predictions = await loop.run_in_executor(
            None, 
            self.audio_classifier.predict, 
            audio_bytes
        )
        
        # Update detection history with best confidence for each species
        for pred in predictions:
            species_id = pred.get("species_id")
            if species_id is None:
                continue
                
            confidence = pred.get("confidence", 0)
            
            # Keep the prediction with best confidence for each species
            if species_id not in self.detection_history or confidence > self.detection_history[species_id].get("confidence", 0):
                self.detection_history[species_id] = {
                    "species_id": species_id,
                    "common_name": pred.get("common_name", "Unknown"),
                    "scientific_name": pred.get("scientific_name", ""),
                    "confidence": confidence,
                }
        
        return predictions
    
    def get_aggregated_results(self) -> List[Dict[str, Any]]:
        """Get all detected species sorted by best confidence."""
        results = list(self.detection_history.values())
        return sorted(results, key=lambda x: x["confidence"], reverse=True)


@router.websocket("/ws/identify/audio")
async def realtime_audio_identification(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio identification.
    
    Protocol:
    - Client connects and starts sending audio chunks
    - Server processes each chunk and sends back detections
    - Client can send JSON messages with base64-encoded audio:
      {"type": "audio_chunk", "data": "<base64-encoded-audio>"}
    - Server responds with detections:
      {"type": "detection", "predictions": [...], "aggregated": [...]}
    - Client sends {"type": "stop"} to end session
    """
    await websocket.accept()
    
    # Get the audio classifier from app state
    audio_classifier = websocket.app.state.audio_classifier
    
    session = RealtimeSession(websocket, audio_classifier)
    
    logger.info("Real-time session started")
    
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Real-time identification ready",
            "chunk_duration_ms": 3000,
        })
        
        while session.is_active:
            try:
                # Receive message from client
                message = await websocket.receive()
                
                if message["type"] == "websocket.disconnect":
                    break
                
                if "text" in message:
                    data = json.loads(message["text"])
                    msg_type = data.get("type", "")
                    
                    if msg_type == "audio_chunk":
                        # Decode base64 audio
                        audio_base64 = data.get("data", "")
                        if audio_base64:
                            try:
                                audio_bytes = base64.b64decode(audio_base64)
                                
                                # Process the audio chunk
                                predictions = await session.process_audio_chunk(audio_bytes)
                                
                                # Get aggregated results (best from entire session)
                                aggregated = session.get_aggregated_results()
                                
                                # Send results back
                                await websocket.send_json({
                                    "type": "detection",
                                    "predictions": predictions[:5],  # Current chunk's top 5
                                    "aggregated": aggregated[:10],   # Session's top 10
                                    "timestamp": datetime.now().isoformat(),
                                })
                                
                                if predictions:
                                    top = predictions[0]
                                    logger.debug("Detected: %s (%.1f%%)", top.get('common_name'), top.get('confidence', 0) * 100)
                                
                            except Exception as e:
                                await websocket.send_json({
                                    "type": "error",
                                    "message": f"Error processing audio: {str(e)}",
                                })
                    
                    elif msg_type == "stop":
                        # End session, send final results
                        aggregated = session.get_aggregated_results()
                        await websocket.send_json({
                            "type": "session_end",
                            "aggregated": aggregated,
                            "message": "Session ended",
                        })
                        session.is_active = False
                    
                    elif msg_type == "ping":
                        await websocket.send_json({"type": "pong"})
                
                elif "bytes" in message:
                    # Handle raw binary audio data
                    audio_bytes = message["bytes"]
                    predictions = await session.process_audio_chunk(audio_bytes)
                    aggregated = session.get_aggregated_results()
                    
                    await websocket.send_json({
                        "type": "detection",
                        "predictions": predictions[:5],
                        "aggregated": aggregated[:10],
                        "timestamp": datetime.now().isoformat(),
                    })
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error", 
                    "message": "Invalid JSON"
                })
            except Exception as e:
                logger.error("WebSocket error: %s", e)
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                
    except Exception as e:
        logger.error("WebSocket session error: %s", e)
    finally:
        logger.info("Real-time session ended")


@router.get("/status")
async def realtime_status():
    """Check if real-time identification is available."""
    return {
        "available": True,
        "protocol": "websocket",
        "endpoint": "/api/v1/realtime/ws/identify/audio",
        "chunk_duration_recommended_ms": 3000,
        "format": "webm/opus or wav",
    }
