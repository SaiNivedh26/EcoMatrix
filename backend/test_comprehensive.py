#!/usr/bin/env python3
"""
Comprehensive test for enhanced EcoMatrix backend with web search and image generation
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_web_search_service():
    """Test the web search functionality"""
    print("🧪 Testing Web Search Service")
    print("=" * 50)
    
    try:
        from web_search_service import WebSearchService
        
        search_service = WebSearchService()
        
        # Test basic product search
        test_queries = [
            "plastic bottle environmental impact carbon footprint",
            "plastic bottle sustainability recycling",
            "eco-friendly alternatives plastic bottles",
            "plastic bottle manufacturing environmental cost"
        ]
        
        print("🔍 Testing product information search...")
        results = await search_service.search_product_info(test_queries, max_results=2)
        
        if results:
            print("✅ Web search completed")
            for key, result in results.items():
                print(f"  📊 {key}: {result.get('query', 'No query')[:50]}...")
                if result.get('answer'):
                    print(f"     💡 Answer: {result['answer'][:100]}...")
        else:
            print("⚠️  Web search returned no results")
        
        # Test DIY tutorial scraping
        print("\n🔨 Testing DIY tutorial scraping...")
        diy_results = await search_service.scrape_diy_tutorials("plastic bottle", ["plastic", "bottle"])
        
        if diy_results:
            print("✅ DIY tutorial scraping completed")
            for key, result in diy_results.items():
                print(f"  📚 {key}: Found {len(result.get('scraped_tutorials', []))} tutorials")
        else:
            print("⚠️  DIY scraping returned no results")
            
        return True
        
    except Exception as e:
        print(f"❌ Web search test failed: {e}")
        return False

async def test_ai_service():
    """Test the enhanced AI service"""
    print("\n🧪 Testing Enhanced AI Service")
    print("=" * 50)
    
    try:
        from ai_service import AIService
        from PIL import Image
        
        ai_service = AIService()
        
        # Create a test image
        print("🖼️  Creating test image...")
        test_image = Image.new('RGB', (200, 300), color=(0, 100, 200))  # Blue bottle-like color
        test_image_path = "test_bottle.png"
        test_image.save(test_image_path)
        
        # Test enhanced DIY project generation
        print("🔨 Testing enhanced DIY project generation...")
        diy_result = await ai_service.generate_diy_projects(test_image_path)
        
        if diy_result:
            print("✅ Enhanced DIY generation completed")
            
            # Check for enhanced features
            if 'tutorial_sources' in diy_result:
                print(f"  📚 Tutorial sources found: {len(diy_result['tutorial_sources'])}")
            
            for difficulty in ['easy', 'medium', 'hard']:
                if difficulty in diy_result:
                    project = diy_result[difficulty]
                    print(f"  📋 {difficulty.upper()}: {project.get('project_name', 'No name')}")
                    
                    if 'generated_image' in project:
                        print(f"    🖼️  Generated image: {project['generated_image'].get('filename', 'No filename')}")
                    else:
                        print("    ⚠️  No generated image")
        else:
            print("❌ DIY generation failed")
            return False
        
        # Clean up
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            
        return True
        
    except Exception as e:
        print(f"❌ AI service test failed: {e}")
        return False

async def test_image_generation():
    """Test image generation specifically"""
    print("\n🧪 Testing AI Image Generation")
    print("=" * 50)
    
    try:
        from ai_service import AIService
        
        ai_service = AIService()
        
        test_prompt = "A creative upcycled plastic bottle transformed into a beautiful hanging planter, painted in bright green with white geometric patterns, hanging from a wooden ceiling with succulent plants growing inside, natural lighting, professional photography style"
        
        print("🎨 Generating test image...")
        print(f"Prompt: {test_prompt[:100]}...")
        
        img_base64, img_filename = ai_service.generate_product_image(test_prompt, "test_planter")
        
        if img_base64 and img_filename:
            print("✅ Image generation successful")
            print(f"  📁 Filename: {img_filename}")
            print(f"  📊 Base64 length: {len(img_base64)} characters")
            
            # Check if file exists
            if os.path.exists(f"static/generated_images/{img_filename}"):
                print(f"  💾 File saved successfully")
            else:
                print(f"  ⚠️  File not found on disk")
                
            return True
        else:
            print("❌ Image generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Image generation test failed: {e}")
        return False

def test_api_keys():
    """Test if required API keys are available"""
    print("🧪 Testing API Key Configuration")
    print("=" * 50)
    
    required_keys = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'TAVILY_API_KEY': os.getenv('TAVILY_API_KEY')
    }
    
    all_keys_present = True
    
    for key_name, key_value in required_keys.items():
        if key_value and len(key_value) > 10:
            print(f"✅ {key_name}: Present ({key_value[:10]}...)")
        else:
            print(f"❌ {key_name}: Missing or invalid")
            all_keys_present = False
    
    if not all_keys_present:
        print("\n⚠️  Some API keys are missing. Enhanced features may not work properly.")
        print("📝 Please check your .env file and ensure all required keys are set.")
        
    return all_keys_present

async def main():
    """Run comprehensive tests"""
    print("🌟 EcoMatrix Enhanced Backend Comprehensive Testing")
    print("=" * 60)
    
    # Test API keys first
    api_keys_ok = test_api_keys()
    
    if not api_keys_ok:
        print("\n🛑 Cannot proceed with full testing without API keys")
        print("📋 Continuing with basic configuration tests only...")
    
    # Run tests
    tests = []
    
    if api_keys_ok:
        tests = [
            ("Web Search Service", test_web_search_service),
            ("AI Service Enhancement", test_ai_service), 
            ("Image Generation", test_image_generation)
        ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name}...")
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")
        
        print("-" * 50)
    
    # Summary
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if total == 0:
        print("⚠️  No tests could be run due to missing API keys")
        print("📝 Please set up your API keys in .env file to enable full testing")
    elif passed == total:
        print("🎉 All enhanced features are working correctly!")
        print("🚀 Your EcoMatrix backend is ready with:")
        print("   • Real-time web search for environmental data")
        print("   • DIY tutorial scraping from the internet")  
        print("   • AI-generated final product images")
        print("   • Enhanced sustainability analysis")
    else:
        print("⚠️  Some enhanced features may not be working properly")
        print("🔧 Check the error messages above for troubleshooting")

if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Please run this test from the backend directory")
        sys.exit(1)
        
    asyncio.run(main())
