#!/usr/bin/env python3
"""
Quick test script for EcoMatrix Backend
Tests basic functionality and API endpoints
"""

import requests
import json
import sys
import os
from pathlib import Path

def test_health_endpoint():
    """Test health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_ui_endpoint():
    """Test UI endpoint"""
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200 and "EcoMatrix" in response.text:
            print("✅ UI endpoint working")
            return True
        else:
            print(f"❌ UI endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ UI test error: {e}")
        return False

def test_api_info():
    """Test API info endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API info endpoint working")
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Features: {len(data.get('features', []))} available")
            return True
        else:
            print(f"❌ API info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API info error: {e}")
        return False

def check_environment():
    """Check environment setup"""
    print("🔍 Checking environment setup...")
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file exists")
        with open('.env', 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY' in content and 'your_gemini_api_key_here' not in content:
                print("✅ Gemini API key configured")
            else:
                print("⚠️  Please configure your Gemini API key in .env file")
    else:
        print("❌ .env file missing")
    
    # Check directories
    dirs = ['uploads', 'temp', 'static']
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
    
    # Check requirements
    try:
        import fastapi
        import google.generativeai
        import uvicorn
        print("✅ Main dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")

def main():
    print("🧪 EcoMatrix Backend Test Suite")
    print("=" * 40)
    
    # Check environment first
    check_environment()
    print()
    
    # Test endpoints
    print("🌐 Testing API endpoints...")
    
    tests = [
        test_health_endpoint,
        test_ui_endpoint,
        test_api_info
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        else:
            break  # Stop on first failure
    
    print()
    print("=" * 40)
    if passed == len(tests):
        print("🎉 All tests passed! Backend is working correctly.")
        print()
        print("🚀 You can now:")
        print("   • Visit http://localhost:8000 for the web UI")
        print("   • Check http://localhost:8000/docs for API documentation")
        print("   • Use the /analyze-product and /analyze-diy endpoints")
    else:
        print(f"❌ {passed}/{len(tests)} tests passed")
        print()
        print("🔧 To fix issues:")
        print("   • Make sure the server is running: python main.py")
        print("   • Check your .env file configuration")
        print("   • Verify all dependencies are installed")

if __name__ == "__main__":
    main()
