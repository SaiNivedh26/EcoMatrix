#!/usr/bin/env python3
"""
Simple test script for EcoMatrix API
"""

import requests
import json
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
        return False

def test_web_interface():
    """Test web interface"""
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Web interface accessible")
            return True
        else:
            print(f"❌ Web interface failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        return False

def test_product_analysis():
    """Test product analysis endpoint with a sample image"""
    print("\n🧪 Testing Product Analysis...")
    
    # Create a simple test image if it doesn't exist
    test_image_path = Path("test_image.jpg")
    if not test_image_path.exists():
        try:
            from PIL import Image
            import io
            
            # Create a simple colored image for testing
            img = Image.new('RGB', (300, 200), color='green')
            img.save(test_image_path, 'JPEG')
            print(f"   Created test image: {test_image_path}")
        except ImportError:
            print("   ⚠️ Pillow not available, skipping image creation")
            return False
    
    if test_image_path.exists():
        try:
            with open(test_image_path, 'rb') as f:
                files = {'file': ('test_image.jpg', f, 'image/jpeg')}
                response = requests.post(f"{BASE_URL}/analyze-product", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Product analysis successful")
                    print(f"   Product: {result.get('product_details', {}).get('product_name', 'N/A')}")
                    print(f"   Sustainability Score: {result.get('environmental_analysis', {}).get('sustainability_score', 'N/A')}/10")
                    return True
                else:
                    print(f"❌ Product analysis failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    return False
        except Exception as e:
            print(f"❌ Error during product analysis: {e}")
            return False
    else:
        print("   ⚠️ No test image available")
        return False

def test_diy_analysis():
    """Test DIY analysis endpoint"""
    print("\n🔨 Testing DIY Analysis...")
    
    test_image_path = Path("test_image.jpg")
    if test_image_path.exists():
        try:
            with open(test_image_path, 'rb') as f:
                files = {'file': ('test_image.jpg', f, 'image/jpeg')}
                response = requests.post(f"{BASE_URL}/analyze-diy", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ DIY analysis successful")
                    projects = result.get('projects', {})
                    print(f"   Generated {len(projects)} project ideas")
                    for difficulty, project in projects.items():
                        print(f"   - {difficulty.title()}: {project.get('project_name', 'N/A')}")
                    return True
                else:
                    print(f"❌ DIY analysis failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    return False
        except Exception as e:
            print(f"❌ Error during DIY analysis: {e}")
            return False
    else:
        print("   ⚠️ No test image available")
        return False

def main():
    """Run all tests"""
    print("🚀 EcoMatrix API Test Suite")
    print("=" * 40)
    
    # Check if server is running
    health_ok = test_health()
    if not health_ok:
        print("\n💡 To start the server, run:")
        print("   cd backend")
        print("   python main.py")
        return
    
    # Test web interface
    web_ok = test_web_interface()
    
    # Test API endpoints (only if GEMINI_API_KEY is set)
    if os.getenv('GEMINI_API_KEY'):
        product_ok = test_product_analysis()
        diy_ok = test_diy_analysis()
        
        print("\n" + "=" * 40)
        print("📊 Test Results:")
        print(f"   Health Check: {'✅' if health_ok else '❌'}")
        print(f"   Web Interface: {'✅' if web_ok else '❌'}")
        print(f"   Product Analysis: {'✅' if product_ok else '❌'}")
        print(f"   DIY Analysis: {'✅' if diy_ok else '❌'}")
        
        if all([health_ok, web_ok, product_ok, diy_ok]):
            print("\n🎉 All tests passed! Your EcoMatrix backend is working correctly.")
            print(f"🌐 Open your browser to: {BASE_URL}")
        else:
            print("\n⚠️ Some tests failed. Check the errors above.")
    else:
        print("\n⚠️ GEMINI_API_KEY not found in environment variables.")
        print("   Set your API key to test the full functionality:")
        print("   export GEMINI_API_KEY='your-api-key-here'")
        
    # Cleanup
    test_image_path = Path("test_image.jpg")
    if test_image_path.exists():
        test_image_path.unlink()
        print(f"\n🧹 Cleaned up test image")

if __name__ == "__main__":
    main()
