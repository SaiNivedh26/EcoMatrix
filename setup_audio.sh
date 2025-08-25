#!/bin/bash

echo "🎤 Setting up Audio Dependencies for EcoMatrix Voice Testing"
echo "=========================================================="

# Check if we're on Ubuntu/Debian
if command -v apt-get &> /dev/null; then
    echo "📦 Installing system audio dependencies (Ubuntu/Debian)..."
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev python3-pyaudio espeak espeak-data libespeak1 libespeak-dev flac
    
elif command -v yum &> /dev/null; then
    echo "📦 Installing system audio dependencies (CentOS/RHEL)..."
    sudo yum install -y portaudio-devel espeak espeak-devel flac
    
elif command -v pacman &> /dev/null; then
    echo "📦 Installing system audio dependencies (Arch Linux)..."
    sudo pacman -S portaudio espeak espeak-ng flac
    
else
    echo "⚠️  Could not detect package manager. Please install manually:"
    echo "   - portaudio development libraries"
    echo "   - espeak or espeak-ng"
    echo "   - flac"
fi

echo ""
echo "🐍 Installing Python audio packages..."

# Install Python packages
pip install --upgrade pip
pip install pyaudio speechrecognition pyttsx3

echo ""
echo "🧪 Testing audio setup..."

# Test microphone
python3 -c "
import pyaudio
import speech_recognition as sr

print('🎤 Testing microphone access...')
try:
    audio = pyaudio.PyAudio()
    print(f'✅ PyAudio initialized. Found {audio.get_device_count()} audio devices.')
    audio.terminate()
    
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    print('✅ Speech recognition and microphone access working!')
    
except Exception as e:
    print(f'❌ Audio test failed: {e}')
    print('You may need to install additional system packages.')
"

# Test TTS
python3 -c "
import pyttsx3

print('🗣️ Testing text-to-speech...')
try:
    engine = pyttsx3.init()
    print('✅ TTS engine initialized successfully!')
    engine.say('Audio setup complete!')
    engine.runAndWait()
except Exception as e:
    print(f'❌ TTS test failed: {e}')
    print('TTS may not work, but speech recognition should still function.')
"

echo ""
echo "✅ Audio setup complete!"
echo ""
echo "🚀 You can now run the voice test clients:"
echo "   python simple_voice_test.py       # Simple command-line interface"
echo "   python local_voice_client.py      # GUI interface with tkinter"
echo ""
echo "📝 Make sure to start the server first:"
echo "   python main.py"

