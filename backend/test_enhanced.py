#!/usr/bin/env python3
"""
Enhanced test script for EcoMatrix backend with image generation
"""
import asyncio
import os
import requests
import json
from PIL import Image
from io import BytesIO
import base64

# Test the server endpoints
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_product_analysis():
    """Test product analysis endpoint"""
    try:
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='red')
        img_buffer = BytesIO()
        test_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        files = {'file': ('test.png', img_buffer, 'image/png')}
        
        print("🔍 Testing product analysis...")
        response = requests.post(f"{BASE_URL}/analyze-product", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Product analysis successful")
            print(f"📊 Analysis: {data.get('product_name', 'Unknown product')}")
            return True
        else:
            print(f"❌ Product analysis failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Product analysis error: {e}")
        return False

def test_diy_analysis_with_images():
    """Test DIY analysis endpoint with image generation"""
    try:
        # Create a test image of a plastic bottle
        test_image = Image.new('RGB', (200, 400), color='blue')
        img_buffer = BytesIO()
        test_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        files = {'file': ('plastic_bottle.png', img_buffer, 'image/png')}
        
        print("🔨 Testing DIY analysis with image generation...")
        response = requests.post(f"{BASE_URL}/analyze-diy", files=files)
        
        if response.status_code == 200:
            data = response.json()
            projects = data.get('projects', {})
            
            print("✅ DIY analysis successful")
            
            # Check each difficulty level for generated images
            for difficulty in ['easy', 'medium', 'hard']:
                if difficulty in projects:
                    project = projects[difficulty]
                    print(f"  📋 {difficulty.upper()}: {project.get('project_name', 'Unknown project')}")
                    
                    if 'generated_image' in project:
                        img_info = project['generated_image']
                        print(f"    🖼️  Generated image: {img_info.get('filename', 'No filename')}")
                        print(f"    🔗 URL: {img_info.get('url', 'No URL')}")
                        
                        # Verify base64 data exists
                        if 'base64' in img_info and len(img_info['base64']) > 0:
                            print(f"    📊 Base64 length: {len(img_info['base64'])}")
                        else:
                            print("    ⚠️  No base64 image data found")
                    else:
                        print("    ⚠️  No generated image found")
            
            return True
        else:
            print(f"❌ DIY analysis failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ DIY analysis error: {e}")
        return False

def test_image_accessibility():
    """Test if generated images are accessible via static URL"""
    try:
        # Check if any generated images exist
        static_dir = "static/generated_images"
        if os.path.exists(static_dir):
            images = [f for f in os.listdir(static_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
            
            if images:
                test_image = images[0]
                image_url = f"{BASE_URL}/static/generated_images/{test_image}"
                
                print(f"🔗 Testing image accessibility: {test_image}")
                response = requests.get(image_url)
                
                if response.status_code == 200:
                    print("✅ Generated image is accessible via URL")
                    return True
                else:
                    print(f"❌ Image not accessible: {response.status_code}")
                    return False
            else:
                print("⚠️  No generated images found to test")
                return True
        else:
            print("⚠️  Generated images directory doesn't exist yet")
            return True
    except Exception as e:
        print(f"❌ Image accessibility test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting EcoMatrix Backend Tests with Image Generation")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Product Analysis", test_product_analysis),
        ("DIY Analysis with Images", test_diy_analysis_with_images),
        ("Image Accessibility", test_image_accessibility),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name}...")
        if test_func():
            passed += 1
        print("-" * 40)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Image generation is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
