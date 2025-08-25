#!/bin/bash

# EcoMatrix ADK Agent Framework Startup Script

echo "🤖 EcoMatrix ADK Agent Framework"
echo "================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Creating .env from template..."
    cp env_example.txt .env
    echo "   Please edit .env with your API keys before running again."
    echo "   Required: GEMINI_API_KEY"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=.*[^_here]" .env; then
    echo "❌ Error: GEMINI_API_KEY not configured in .env file"
    echo "   Please edit .env and add your Gemini API key"
    exit 1
fi

echo ""
echo "🚀 Starting EcoMatrix ADK Agent Framework..."
echo ""
echo "📍 Endpoints will be available at:"
echo "   🌐 HTTP API: http://localhost:8000"
echo "   🔌 WebSocket: ws://localhost:8000/media"
echo "   📥 Passthru: http://localhost:8000/passthru"
echo "   🏥 Health: http://localhost:8000/health"
echo ""
echo "🔧 For Exotel integration, configure your applet with:"
echo "   WebSocket URL: ws://YOUR_SERVER_IP:8000/media"
echo "   Passthru URL: http://YOUR_SERVER_IP:8000/passthru"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================="

# Start the server
python main.py

