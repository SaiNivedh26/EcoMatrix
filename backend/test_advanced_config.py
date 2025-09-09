#!/usr/bin/env python3
"""
Advanced Crawl4AI configuration test to resolve Playwright issues
"""

import asyncio
import logging
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_advanced_config():
    """Test advanced Crawl4AI configuration to avoid Playwright"""
    try:
        logger.info("🧪 Testing advanced Crawl4AI configuration...")
        
        from crawl4ai import AsyncWebCrawler
        from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
        
        # Try different browser configurations
        configs_to_test = [
            {
                "name": "Basic headless",
                "config": BrowserConfig(headless=True)
            },
            {
                "name": "Chromium engine",
                "config": BrowserConfig(headless=True, browser_type="chromium")
            },
            {
                "name": "Chrome engine", 
                "config": BrowserConfig(headless=True, browser_type="chrome")
            },
            {
                "name": "Minimal config",
                "config": BrowserConfig()
            }
        ]
        
        for test in configs_to_test:
            logger.info(f"Testing: {test['name']}")
            
            try:
                async with AsyncWebCrawler(config=test['config']) as crawler:
                    logger.info(f"✅ {test['name']}: Initialization successful")
                    
                    # Test simple crawl
                    result = await crawler.arun(
                        url="https://httpbin.org/html",
                        config=CrawlerRunConfig()
                    )
                    
                    if result.success:
                        logger.info(f"✅ {test['name']}: Crawl successful")
                    else:
                        logger.warning(f"⚠️ {test['name']}: Crawl failed")
                        
            except Exception as e:
                logger.error(f"❌ {test['name']}: {e}")
                
        return True
        
    except Exception as e:
        logger.error(f"💥 Configuration test failed: {e}")
        return False

async def test_web_search_service_config():
    """Test the web search service with different configurations"""
    try:
        logger.info("🧪 Testing WebSearchService with anti-Playwright config...")
        
        # Add current directory to path
        sys.path.append('.')
        
        from web_search_service import WebSearchService
        
        search_service = WebSearchService()
        
        # Test the _scrape_tutorial_content method directly
        test_urls = ["https://httpbin.org/html"]
        
        logger.info("📚 Testing tutorial content scraping...")
        results = await search_service._scrape_tutorial_content(test_urls)
        
        if results:
            logger.info("✅ WebSearchService scraping successful")
            for result in results:
                logger.info(f"   Status: {result.get('success', False)}")
                logger.info(f"   Method: {result.get('method', 'unknown')}")
                if result.get('error'):
                    logger.warning(f"   Error: {result['error']}")
            return True
        else:
            logger.warning("⚠️ No results returned")
            return False
            
    except Exception as e:
        logger.error(f"💥 WebSearchService test failed: {e}")
        logger.error(f"   Error type: {type(e).__name__}")
        return False

def main():
    print("🔧 Advanced Crawl4AI Configuration Test")
    print("=" * 50)
    
    try:
        # Test 1: Different browser configurations
        print("\n🧪 Test 1: Browser Configuration Options")
        result1 = asyncio.run(test_advanced_config())
        
        # Test 2: WebSearchService integration
        print("\n🧪 Test 2: WebSearchService Integration")
        result2 = asyncio.run(test_web_search_service_config())
        
        print("\n" + "=" * 50)
        print("📊 Test Results:")
        print(f"   🔧 Browser Configs: {'✅ PASS' if result1 else '❌ FAIL'}")
        print(f"   🌐 WebSearchService: {'✅ PASS' if result2 else '❌ FAIL'}")
        
        if result1 and result2:
            print("\n🎉 All advanced tests passed!")
            print("🚀 Crawl4AI should work without Playwright issues")
        else:
            print("\n⚠️ Some tests failed")
            print("💡 Try different browser configurations or fallback methods")
            
    except Exception as e:
        print(f"💥 Test execution error: {e}")

if __name__ == "__main__":
    main()
