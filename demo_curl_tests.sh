#!/bin/bash

# EcoMatrix ADK Agent Framework - cURL Test Suite
# Test the REST API endpoints

SERVER="localhost:8000"

echo "🧪 EcoMatrix ADK Agent Framework - API Tests"
echo "============================================="

echo ""
echo "1️⃣  Testing Root Endpoint"
echo "curl http://$SERVER/"
curl -s http://$SERVER/ | jq '.' || echo "Response received (jq not available)"

echo ""
echo "2️⃣  Testing Health Endpoint"
echo "curl http://$SERVER/health"
curl -s http://$SERVER/health | jq '.' || echo "Response received (jq not available)"

echo ""
echo "3️⃣  Testing Passthru Endpoint (Flat Format)"
echo "curl -X POST \"http://$SERVER/passthru?CallSid=test123&Stream[Status]=completed\""
curl -s -X POST "http://$SERVER/passthru?CallSid=test_call_123&Direction=inbound&From=%2B1234567890&To=%2B0987654321&Stream[StreamSID]=test_stream_456&Stream[Status]=completed&Stream[Duration]=30&Stream[StreamUrl]=ws://$SERVER/media&Stream[DisconnectedBy]=user" | jq '.' || echo "Response received (jq not available)"

echo ""
echo "4️⃣  Testing Passthru Endpoint (JSON Format)"
JSON_STREAM='{"StreamSID":"test_stream_789","Status":"completed","Duration":"25","StreamUrl":"ws://localhost:8000/media","DisconnectedBy":"bot"}'
echo "curl -X POST \"http://$SERVER/passthru\" with JSON Stream data"
curl -s -X POST "http://$SERVER/passthru" \
  --data-urlencode "CallSid=test_call_456" \
  --data-urlencode "Direction=inbound" \
  --data-urlencode "From=+1234567890" \
  --data-urlencode "To=+0987654321" \
  --data-urlencode "Stream=$JSON_STREAM" | jq '.' || echo "Response received (jq not available)"

echo ""
echo "✅ API Tests Complete!"
echo ""
echo "🔌 For WebSocket testing, use the Python test script:"
echo "   python test_server.py"
echo ""
echo "🚀 To start the full server:"
echo "   python main.py"
echo "   # or"
echo "   ./start_server.sh"

