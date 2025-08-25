#!/usr/bin/env python3
"""
EcoMatrix ADK Agent Framework with FastAPI and Exotel Integration
Bidirectional streaming voice agent with location services
"""

import asyncio
import websockets
import json
import logging
import base64
import time
import struct
import ssl
import os
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from agents.agents import EcoMatrixAgent
from tools.map import LocationTool
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="EcoMatrix ADK Agent Framework",
    description="Voice agent with Exotel integration for location services",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExotelStreamManager:
    """Manages WebSocket connections and streaming with Exotel"""
    
    def __init__(self):
        self.connections: Dict[str, Dict[str, Any]] = {}
        self.agent = EcoMatrixAgent()
        self.location_tool = LocationTool()
        
        # Audio buffering for better conversation flow
        self.audio_buffers: Dict[str, bytes] = {}
        self.buffer_size_ms = Config.BUFFER_SIZE_MS
        self.sample_rate = Config.SAMPLE_RATE
        self.bytes_per_chunk = int((self.sample_rate * 2 * self.buffer_size_ms) / 1000)
        
        logger.info("🤖 EcoMatrix Agent Framework initialized!")
        logger.info(f"🔊 Audio buffering: {self.buffer_size_ms}ms chunks ({self.bytes_per_chunk} bytes)")

    async def handle_exotel_websocket(self, websocket: WebSocket):
        """Handle incoming WebSocket connection from Exotel"""
        stream_id = "unknown"
        
        try:
            await websocket.accept()
            logger.info(f"📞 NEW CALL from Exotel: {websocket.client}")
            
            async for message in websocket.iter_text():
                try:
                    data = json.loads(message)
                    event = data.get("event", "")
                    
                    # Extract stream ID
                    if "streamSid" in data:
                        stream_id = data["streamSid"]
                    elif "stream_sid" in data:
                        stream_id = data["stream_sid"]
                    
                    logger.info(f"🆔 STREAM ID: {stream_id}")
                    logger.info(f"🎯 EVENT: '{event}' for {stream_id}")
                    
                    # Store connection
                    if stream_id not in self.connections:
                        self.connections[stream_id] = {
                            "websocket": websocket,
                            "start_time": time.time(),
                            "agent_session": await self.agent.create_session(stream_id)
                        }
                        logger.info(f"📞 NEW CONNECTION: {stream_id}")
                    
                    # Handle events
                    if event == "connected":
                        await self.handle_connected(stream_id, data)
                    elif event == "start":
                        await self.handle_start(stream_id, data)
                    elif event == "media":
                        await self.handle_media(stream_id, data)
                    elif event == "mark":
                        await self.handle_mark(stream_id, data)
                    elif event == "clear":
                        await self.handle_clear(stream_id, data)
                    elif event == "stop":
                        await self.handle_stop(stream_id, data)
                        break
                    else:
                        logger.info(f"🔄 UNHANDLED EVENT: {event} for {stream_id}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON decode error: {e}")
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
                    
        except WebSocketDisconnect:
            logger.info(f"🔚 CONNECTION CLOSED: {stream_id}")
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
        finally:
            await self.cleanup_connection(stream_id)

    async def handle_connected(self, stream_id: str, data: dict):
        """Handle Exotel connected event"""
        logger.info(f"✅ EXOTEL CONNECTED: {stream_id}")
        
        # Send initial greeting
        await self.send_initial_greeting(stream_id)

    async def handle_start(self, stream_id: str, data: dict):
        """Handle Exotel start event"""
        logger.info(f"🚀 CALL STARTED: {stream_id}")

    async def handle_media(self, stream_id: str, data: dict):
        """Handle incoming audio from customer"""
        if stream_id not in self.connections:
            logger.warning(f"⚠️ No connection for {stream_id}")
            return
            
        media = data.get("media", {})
        audio_payload = media.get("payload", "")
        
        if audio_payload:
            try:
                # Decode PCM audio from Exotel
                audio_data = base64.b64decode(audio_payload)
                
                # Process with agent
                response_audio = await self.agent.process_audio(
                    stream_id, 
                    audio_data,
                    self.location_tool
                )
                
                if response_audio:
                    await self.send_audio_to_exotel(stream_id, response_audio)
                    
            except Exception as e:
                logger.error(f"❌ Error processing audio: {e}")

    async def handle_clear(self, stream_id: str, data: dict):
        """Handle Exotel clear event - customer interrupted"""
        logger.info(f"🧹 CUSTOMER INTERRUPTED: {stream_id}")
        
        if stream_id in self.connections:
            await self.agent.handle_interruption(stream_id)

    async def handle_stop(self, stream_id: str, data: dict):
        """Handle Exotel stop event"""
        logger.info(f"🛑 CALL ENDED: {stream_id}")

    async def handle_mark(self, stream_id: str, data: dict):
        """Handle Exotel mark event"""
        mark_name = data.get("mark", {}).get("name", "unknown")
        logger.info(f"📍 MARK: {mark_name} for {stream_id}")

    async def send_initial_greeting(self, stream_id: str):
        """Send initial greeting to customer"""
        try:
            greeting_audio = await self.agent.generate_greeting(stream_id)
            if greeting_audio:
                await self.send_audio_to_exotel(stream_id, greeting_audio)
        except Exception as e:
            logger.error(f"❌ Error sending greeting: {e}")

    async def send_audio_to_exotel(self, stream_id: str, audio_data: bytes):
        """Send audio response back to Exotel"""
        try:
            if stream_id not in self.connections:
                return
                
            websocket = self.connections[stream_id]["websocket"]
            audio_b64 = base64.b64encode(audio_data).decode()
            
            message = {
                "event": "media",
                "streamSid": stream_id,
                "media": {
                    "payload": audio_b64,
                    "timestamp": str(int(time.time() * 1000)),
                    "sequenceNumber": str(int(time.time()))
                }
            }
            
            await websocket.send_text(json.dumps(message))
            logger.info(f"📤 SENT AUDIO TO CUSTOMER: {len(audio_data)} bytes")
            
        except Exception as e:
            logger.error(f"❌ Error sending audio: {e}")

    async def cleanup_connection(self, stream_id: str):
        """Clean up connection resources"""
        try:
            if stream_id in self.connections:
                await self.agent.cleanup_session(stream_id)
                del self.connections[stream_id]
                logger.info(f"🧹 CONNECTION CLEANED: {stream_id}")
                
            if stream_id in self.audio_buffers:
                del self.audio_buffers[stream_id]
                
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")

# Global stream manager
stream_manager = ExotelStreamManager()

@app.websocket("/media")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for Exotel media streaming"""
    await stream_manager.handle_exotel_websocket(websocket)

@app.post("/passthru")
async def passthru_handler(request: Request):
    """Handle Exotel passthru webhook"""
    try:
        # Get query parameters
        params = dict(request.query_params)
        
        logger.info(f"📥 PASSTHRU RECEIVED: {params}")
        
        # Extract important parameters
        call_sid = params.get("CallSid", "unknown")
        direction = params.get("Direction", "unknown")
        from_number = params.get("From", "unknown")
        to_number = params.get("To", "unknown")
        
        # Stream-specific parameters
        stream_sid = params.get("Stream[StreamSID]", "")
        stream_status = params.get("Stream[Status]", "")
        stream_duration = params.get("Stream[Duration]", "0")
        stream_url = params.get("Stream[StreamUrl]", "")
        recording_url = params.get("Stream[RecordingUrl]", "")
        disconnected_by = params.get("Stream[DisconnectedBy]", "unknown")
        
        # Handle JSON format if present
        stream_json = params.get("Stream", "")
        if stream_json and stream_json.startswith("{"):
            try:
                stream_data = json.loads(stream_json)
                stream_sid = stream_data.get("StreamSID", stream_sid)
                stream_status = stream_data.get("Status", stream_status)
                stream_duration = stream_data.get("Duration", stream_duration)
                stream_url = stream_data.get("StreamUrl", stream_url)
                recording_url = stream_data.get("RecordingUrl", recording_url)
                disconnected_by = stream_data.get("DisconnectedBy", disconnected_by)
            except json.JSONDecodeError:
                logger.error("❌ Failed to parse Stream JSON")
        
        # Log call details
        logger.info(f"📞 CALL DETAILS:")
        logger.info(f"   Call SID: {call_sid}")
        logger.info(f"   Direction: {direction}")
        logger.info(f"   From: {from_number}")
        logger.info(f"   To: {to_number}")
        logger.info(f"   Stream SID: {stream_sid}")
        logger.info(f"   Stream Status: {stream_status}")
        logger.info(f"   Duration: {stream_duration}s")
        logger.info(f"   Disconnected By: {disconnected_by}")
        
        # Store call metadata for analytics
        call_metadata = {
            "call_sid": call_sid,
            "stream_sid": stream_sid,
            "direction": direction,
            "from_number": from_number,
            "to_number": to_number,
            "status": stream_status,
            "duration": stream_duration,
            "disconnected_by": disconnected_by,
            "recording_url": recording_url,
            "timestamp": datetime.now().isoformat()
        }
        
        # You can store this in a database or send to analytics service
        logger.info(f"📊 CALL METADATA: {json.dumps(call_metadata, indent=2)}")
        
        # Return 200 OK for successful processing
        return JSONResponse(
            status_code=200,
            content={"status": "success", "message": "Passthru processed successfully"}
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing passthru: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "active_connections": len(stream_manager.connections)
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "EcoMatrix ADK Agent Framework",
        "version": "1.0.0",
        "endpoints": {
            "websocket": "/media",
            "passthru": "/passthru",
            "health": "/health"
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("🚀 Starting EcoMatrix ADK Agent Framework")
    logger.info(f"🔗 WebSocket endpoint: ws://{Config.SERVER_HOST}:{Config.SERVER_PORT}/media")
    logger.info(f"📥 Passthru endpoint: http://{Config.SERVER_HOST}:{Config.SERVER_PORT}/passthru")
    
    uvicorn.run(
        "main:app",
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        log_level="info",
        reload=Config.DEBUG
    )

