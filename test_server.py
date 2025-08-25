#!/usr/bin/env python3
"""
Test script for EcoMatrix ADK Agent Framework
Tests WebSocket connections and API endpoints
"""

import asyncio
import websockets
import json
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_HOST = "localhost"
SERVER_PORT = 8000

async def test_websocket_connection():
    """Test WebSocket connection to the media endpoint"""
    try:
        uri = f"ws://{SERVER_HOST}:{SERVER_PORT}/media"
        logger.info(f"🔗 Connecting to WebSocket: {uri}")
        
        async with websockets.connect(uri) as websocket:
            logger.info("✅ WebSocket connected successfully")
            
            # Send a test connected event
            test_message = {
                "event": "connected",
                "streamSid": "test_stream_123",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(test_message))
            logger.info("📤 Sent connected event")
            
            # Send a test start event
            start_message = {
                "event": "start",
                "streamSid": "test_stream_123",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(start_message))
            logger.info("📤 Sent start event")
            
            # Send a test media event (simulated audio)
            media_message = {
                "event": "media",
                "streamSid": "test_stream_123",
                "media": {
                    "payload": "dGVzdCBhdWRpbyBkYXRh",  # base64 encoded "test audio data"
                    "timestamp": str(int(datetime.now().timestamp() * 1000)),
                    "sequenceNumber": "1"
                }
            }
            
            await websocket.send(json.dumps(media_message))
            logger.info("📤 Sent media event")
            
            # Wait for potential responses
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                logger.info(f"📥 Received response: {response}")
            except asyncio.TimeoutError:
                logger.info("⏱️ No immediate response (this is normal)")
            
            # Send stop event
            stop_message = {
                "event": "stop",
                "streamSid": "test_stream_123",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(stop_message))
            logger.info("📤 Sent stop event")
            
            logger.info("✅ WebSocket test completed successfully")
            
    except Exception as e:
        logger.error(f"❌ WebSocket test failed: {e}")

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        url = f"http://{SERVER_HOST}:{SERVER_PORT}/health"
        logger.info(f"🏥 Testing health endpoint: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Health check passed")
            logger.info(f"   Status: {data.get('status')}")
            logger.info(f"   Active connections: {data.get('active_connections')}")
            logger.info(f"   Timestamp: {data.get('timestamp')}")
        else:
            logger.error(f"❌ Health check failed with status: {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Health endpoint test failed: {e}")

def test_passthru_endpoint():
    """Test the passthru webhook endpoint"""
    try:
        url = f"http://{SERVER_HOST}:{SERVER_PORT}/passthru"
        logger.info(f"📥 Testing passthru endpoint: {url}")
        
        # Test with query parameters (flat format)
        params = {
            "CallSid": "test_call_123",
            "Direction": "inbound",
            "From": "+1234567890",
            "To": "+0987654321",
            "Stream[StreamSID]": "test_stream_456",
            "Stream[Status]": "completed",
            "Stream[Duration]": "30",
            "Stream[StreamUrl]": f"ws://{SERVER_HOST}:{SERVER_PORT}/media",
            "Stream[DisconnectedBy]": "user"
        }
        
        response = requests.post(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Passthru test (flat format) passed")
            logger.info(f"   Response: {data}")
        else:
            logger.error(f"❌ Passthru test failed with status: {response.status_code}")
        
        # Test with JSON format
        json_params = {
            "CallSid": "test_call_456",
            "Direction": "inbound",
            "From": "+1234567890",
            "To": "+0987654321",
            "Stream": json.dumps({
                "StreamSID": "test_stream_789",
                "Status": "completed",
                "Duration": "25",
                "StreamUrl": f"ws://{SERVER_HOST}:{SERVER_PORT}/media",
                "DisconnectedBy": "bot"
            })
        }
        
        response = requests.post(url, params=json_params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Passthru test (JSON format) passed")
            logger.info(f"   Response: {data}")
        else:
            logger.error(f"❌ Passthru JSON test failed with status: {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Passthru endpoint test failed: {e}")

def test_root_endpoint():
    """Test the root endpoint"""
    try:
        url = f"http://{SERVER_HOST}:{SERVER_PORT}/"
        logger.info(f"🏠 Testing root endpoint: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Root endpoint test passed")
            logger.info(f"   Message: {data.get('message')}")
            logger.info(f"   Version: {data.get('version')}")
        else:
            logger.error(f"❌ Root endpoint test failed with status: {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Root endpoint test failed: {e}")

async def run_all_tests():
    """Run all tests"""
    logger.info("🚀 Starting EcoMatrix ADK Agent Framework Tests")
    logger.info("=" * 60)
    
    # Test HTTP endpoints
    logger.info("\n📡 Testing HTTP Endpoints")
    test_root_endpoint()
    test_health_endpoint()
    test_passthru_endpoint()
    
    # Test WebSocket
    logger.info("\n🔌 Testing WebSocket Connection")
    await test_websocket_connection()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ All tests completed!")
    logger.info("\nNext steps:")
    logger.info("1. Configure your .env file with API keys")
    logger.info("2. Set up Exotel applet with your server URLs:")
    logger.info(f"   WebSocket: ws://your-server-ip:{SERVER_PORT}/media")
    logger.info(f"   Passthru: http://your-server-ip:{SERVER_PORT}/passthru")

if __name__ == "__main__":
    print(f"""
🤖 EcoMatrix ADK Agent Framework Test Suite

Testing server at: {SERVER_HOST}:{SERVER_PORT}

Make sure the server is running before starting tests:
  python main.py

Starting tests in 3 seconds...
    """)
    
    import time
    time.sleep(3)
    
    asyncio.run(run_all_tests())

