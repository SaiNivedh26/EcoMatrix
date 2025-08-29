"""
Web Search Service using Tavily API and Crawl4AI for comprehensive product research
"""
import asyncio
import sys
import logging
import time
from typing import List, Dict, Any, Optional
import aiohttp

# Fix for Windows async subprocess issues with Playwright/Crawl4AI
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from tavily import TavilyClient
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from bs4 import BeautifulSoup
import json
from config import Config

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        """Initialize web search service with Tavily client"""
        self.tavily_client = None
        if Config.TAVILY_API_KEY:
            try:
                self.tavily_client = TavilyClient(api_key=Config.TAVILY_API_KEY)
                logger.info("Tavily client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Tavily client: {e}")
        else:
            logger.warning("TAVILY_API_KEY not found - web search will be limited")

    async def search_product_info(self, search_queries: List[str], max_results: int = 3) -> Dict[str, Any]:
        """
        Search for product information using Tavily API
        
        Args:
            search_queries: List of search queries
            max_results: Maximum results per query
            
        Returns:
            Dictionary containing search results and scraped content
        """
        try:
            logger.info(f"🔍 Starting Tavily search for {len(search_queries)} queries")
            logger.info(f"📋 Search queries: {search_queries}")
            
            if not self.tavily_client:
                logger.warning("⚠️ Tavily client not available - using fallback search")
                return await self._fallback_search(search_queries)

            search_results = {}
            total_results = 0
            
            for i, query in enumerate(search_queries[:4]):  # Limit to 4 queries
                try:
                    logger.info(f"🔎 [{i+1}/{len(search_queries[:4])}] Searching with Tavily: '{query}'")
                    start_time = time.time()
                    
                    # Use Tavily to search
                    response = self.tavily_client.search(
                        query=query,
                        search_depth="advanced",
                        max_results=max_results,
                        include_answer=True,
                        include_raw_content=True
                    )
                    
                    search_time = time.time() - start_time
                    logger.info(f"⏱️ Tavily search completed in {search_time:.2f}s")
                    
                    # Log response details
                    answer = response.get("answer", "")
                    results = response.get("results", [])
                    
                    logger.info(f"📊 Query {i+1} Results:")
                    logger.info(f"   • Answer length: {len(answer)} characters")
                    logger.info(f"   • Number of results: {len(results)}")
                    
                    if answer:
                        logger.info(f"   • Answer preview: {answer[:150]}...")
                    
                    # Log individual results
                    for j, result in enumerate(results[:3]):  # Log first 3 results
                        title = result.get("title", "No title")
                        url = result.get("url", "No URL")
                        content_length = len(result.get("content", ""))
                        logger.info(f"   • Result {j+1}: {title[:50]}... ({url}) - {content_length} chars")
                    
                    search_results[f"query_{i+1}"] = {
                        "query": query,
                        "answer": answer,
                        "results": results,
                        "search_time": search_time,
                        "result_count": len(results)
                    }
                    
                    total_results += len(results)
                    
                    # Add delay between requests
                    logger.info(f"😴 Waiting 0.5s before next query...")
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"❌ Error searching with Tavily for query '{query}': {e}")
                    logger.error(f"   Error type: {type(e).__name__}")
                    search_results[f"query_{i+1}"] = {
                        "query": query,
                        "answer": "Search failed",
                        "results": [],
                        "error": str(e),
                        "search_time": 0,
                        "result_count": 0
                    }

            logger.info(f"✅ Tavily search completed. Total results: {total_results}")
            logger.info(f"📈 Search summary: {len([r for r in search_results.values() if r.get('result_count', 0) > 0])}/{len(search_queries[:4])} queries successful")
            
            return search_results
            
        except Exception as e:
            logger.error(f"💥 Critical error in search_product_info: {e}")
            logger.error(f"   Error type: {type(e).__name__}")
            return await self._fallback_search(search_queries)

    async def scrape_diy_tutorials(self, product_name: str, materials: List[str]) -> Dict[str, Any]:
        """
        Search and scrape DIY tutorial websites for upcycling ideas
        
        Args:
            product_name: Name of the product to upcycle
            materials: List of materials in the product
            
        Returns:
            Dictionary containing DIY tutorial information
        """
        try:
            logger.info(f"🔨 Starting DIY tutorial search for: '{product_name}'")
            logger.info(f"🧱 Using materials: {materials}")
            
            # Generate DIY-focused search queries
            diy_queries = [
                f"DIY upcycle {product_name} tutorial step by step",
                f"how to reuse {product_name} creative ideas",
                f"upcycling {' '.join(materials[:2])} projects instructions",
                f"{product_name} waste reduction crafts tutorial"
            ]
            
            logger.info(f"📋 Generated {len(diy_queries)} DIY search queries:")
            for i, query in enumerate(diy_queries):
                logger.info(f"   {i+1}. {query}")
            
            diy_results = {}
            total_tutorials_found = 0
            
            if self.tavily_client:
                logger.info("🔍 Using Tavily client for DIY tutorial search")
                
                for i, query in enumerate(diy_queries):
                    try:
                        logger.info(f"🔎 [{i+1}/{len(diy_queries)}] Searching DIY tutorials: '{query}'")
                        start_time = time.time()
                        
                        response = self.tavily_client.search(
                            query=query,
                            search_depth="advanced",
                            max_results=5,
                            include_answer=True,
                            include_raw_content=True
                        )
                        
                        search_time = time.time() - start_time
                        logger.info(f"⏱️ DIY search {i+1} completed in {search_time:.2f}s")
                        
                        # Get URLs for detailed scraping
                        results = response.get("results", [])
                        urls = [result.get("url") for result in results[:3]]
                        valid_urls = [url for url in urls if url]
                        
                        logger.info(f"📊 DIY Query {i+1} Results:")
                        logger.info(f"   • Answer: {response.get('answer', 'No answer')[:100]}...")
                        logger.info(f"   • Found {len(results)} results, {len(valid_urls)} valid URLs")
                        
                        for j, url in enumerate(valid_urls):
                            logger.info(f"   • URL {j+1}: {url}")
                        
                        # Scrape detailed content from tutorial websites
                        logger.info(f"🕷️ Starting content scraping for {len(valid_urls)} URLs...")
                        scrape_start_time = time.time()
                        
                        scraped_content = await self._scrape_tutorial_content(valid_urls)
                        
                        scrape_time = time.time() - scrape_start_time
                        successful_scrapes = len([s for s in scraped_content if s.get('success', False)])
                        total_tutorials_found += successful_scrapes
                        
                        logger.info(f"✅ Content scraping completed in {scrape_time:.2f}s")
                        logger.info(f"📈 Scraping results: {successful_scrapes}/{len(valid_urls)} successful")
                        
                        diy_results[f"diy_query_{i+1}"] = {
                            "query": query,
                            "answer": response.get("answer", ""),
                            "urls": valid_urls,
                            "scraped_tutorials": scraped_content,
                            "search_time": search_time,
                            "scrape_time": scrape_time,
                            "successful_scrapes": successful_scrapes
                        }
                        
                        logger.info(f"😴 Waiting 0.5s before next DIY query...")
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"❌ Error searching DIY tutorials for '{query}': {e}")
                        logger.error(f"   Error type: {type(e).__name__}")
                        diy_results[f"diy_query_{i+1}"] = {
                            "query": query,
                            "error": str(e),
                            "search_time": 0,
                            "scrape_time": 0,
                            "successful_scrapes": 0
                        }
                        
                logger.info(f"🎉 DIY tutorial search completed!")
                logger.info(f"📊 Final DIY search summary:")
                logger.info(f"   • Total queries: {len(diy_queries)}")
                logger.info(f"   • Total tutorials found: {total_tutorials_found}")
                logger.info(f"   • Success rate: {total_tutorials_found}/{len(diy_queries)*3:.0f} expected tutorials")
                
            else:
                logger.warning("⚠️ Tavily client not available for DIY search")
            
            return diy_results
            
        except Exception as e:
            logger.error(f"💥 Critical error in scrape_diy_tutorials: {e}")
            logger.error(f"   Error type: {type(e).__name__}")
            return {"error": str(e)}

    async def _scrape_tutorial_content(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Use Crawl4AI to scrape detailed content from tutorial websites
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of scraped content
        """
        scraped_content = []
        
        try:
            logger.info(f"🕷️ Starting Crawl4AI scraping for {len(urls)} URLs")
            
            try:
                # Configure browser properly
                browser_config = BrowserConfig(
                    headless=True,
                    verbose=True,
                    use_playwright=False  # Avoid Playwright subprocess issues
                )
                
                # Configure crawl run settings
                run_config = CrawlerRunConfig(
                    word_count_threshold=50,        # Minimum words per content block
                    exclude_external_links=True,    # Remove external links to focus on content
                    remove_overlay_elements=True,   # Remove popups/modals that interfere
                    process_iframes=True,          # Process iframe content
                    cache_mode=CacheMode.ENABLED   # Use cache for efficiency
                )
                
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    logger.info("🚀 AsyncWebCrawler initialized successfully (Crawl4AI proper config)")
                    
                    for i, url in enumerate(urls):
                        if not url:
                            logger.warning(f"⚠️ Skipping empty URL at position {i}")
                            continue
                            
                        try:
                            logger.info(f"📄 [{i+1}/{len(urls)}] Scraping tutorial content from: {url}")
                            start_time = time.time()
                            
                            result = await crawler.arun(
                                url=url,
                                config=run_config
                            )
                            
                            scrape_time = time.time() - start_time
                            logger.info(f"⏱️ Scraping completed in {scrape_time:.2f}s")
                            
                            if result.success:
                                logger.info("✅ Crawl4AI scraping successful, processing content...")
                                logger.info(f"📊 Status Code: {result.status_code}")
                                
                                # Use Crawl4AI's built-in content processing
                                original_html_length = len(result.html) if result.html else 0
                                cleaned_html_length = len(result.cleaned_html) if result.cleaned_html else 0
                                markdown_length = len(result.markdown.raw_markdown) if result.markdown else 0
                                
                                logger.info(f"📊 Original HTML: {original_html_length:,} characters")
                                logger.info(f"🧹 Cleaned HTML: {cleaned_html_length:,} characters")
                                logger.info(f"� Markdown: {markdown_length:,} characters")
                                
                                # Use the fit_markdown for most relevant content
                                clean_text = ""
                                if result.markdown and result.markdown.fit_markdown:
                                    clean_text = result.markdown.fit_markdown
                                    logger.info(f"✅ Using fit_markdown: {len(clean_text):,} characters")
                                elif result.markdown and result.markdown.raw_markdown:
                                    clean_text = result.markdown.raw_markdown
                                    logger.info(f"✅ Using raw_markdown: {len(clean_text):,} characters")
                                elif result.cleaned_html:
                                    # Fallback to BeautifulSoup if markdown not available
                                    soup = BeautifulSoup(result.cleaned_html, 'html.parser')
                                    clean_text = soup.get_text()
                                    logger.info(f"⚠️ Fallback to text extraction: {len(clean_text):,} characters")
                                else:
                                    logger.warning("⚠️ No usable content found")
                                    clean_text = ""
                                
                                logger.info(f"📝 Clean text: {len(clean_text):,} characters")
                                
                                # Extract steps if possible
                                logger.info("🔍 Extracting tutorial steps...")
                                steps = self._extract_tutorial_steps(clean_text)
                                logger.info(f"📋 Found {len(steps)} tutorial steps")
                                
                                # Extract materials
                                logger.info("🧱 Extracting materials list...")
                                materials = self._extract_materials_list(clean_text)
                                logger.info(f"🛠️ Found {len(materials)} materials")
                                
                                # Extract additional metadata from Crawl4AI result
                                images_found = len(result.media.get("images", [])) if result.media else 0
                                internal_links = len(result.links.get("internal", [])) if result.links else 0
                                external_links = len(result.links.get("external", [])) if result.links else 0
                                
                                logger.info(f"🖼️ Found {images_found} images")
                                logger.info(f"🔗 Found {internal_links} internal links, {external_links} external links")
                                
                                # Log first few steps and materials for verification
                                if steps:
                                    logger.info(f"   First step: {steps[0][:100]}...")
                                if materials:
                                    logger.info(f"   First material: {materials[0]}")
                                
                                scraped_content.append({
                                    "url": url,
                                    "title": getattr(result, 'title', '') or result.metadata.get("title", ""),
                                    "content": clean_text[:2000],  # Limit content length
                                    "steps": steps,
                                    "materials": materials,
                                    "success": True,
                                    "scrape_time": scrape_time,
                                    "status_code": result.status_code,
                                    "original_html_length": original_html_length,
                                    "cleaned_html_length": cleaned_html_length,
                                    "markdown_length": markdown_length,
                                    "clean_text_length": len(clean_text),
                                    "steps_found": len(steps),
                                    "materials_found": len(materials),
                                    "images_found": images_found,
                                    "internal_links_found": internal_links,
                                    "external_links_found": external_links,
                                    "media": result.media if result.media else {},
                                    "links": result.links if result.links else {},
                                    "method": "crawl4ai_proper"
                                })
                                
                                logger.info(f"✅ Successfully processed content from {url}")
                                
                            else:
                                logger.warning(f"❌ Failed to scrape {url}")
                                logger.warning(f"   Error: {getattr(result, 'error_message', 'Unknown error')}")
                                logger.warning(f"   Status Code: {getattr(result, 'status_code', 'Unknown')}")
                                
                                scraped_content.append({
                                    "url": url,
                                    "error": getattr(result, 'error_message', 'Unknown error'),
                                    "status_code": getattr(result, 'status_code', None),
                                    "success": False,
                                    "scrape_time": scrape_time,
                                    "method": "crawl4ai_proper"
                                })
                                
                            # Rate limiting
                            logger.info(f"😴 Waiting 1s before next scrape...")
                            await asyncio.sleep(1)
                            
                        except Exception as e:
                            scrape_time = time.time() - start_time if 'start_time' in locals() else 0
                            logger.error(f"💥 Error scraping {url}: {e}")
                            logger.error(f"   Error type: {type(e).__name__}")
                            scraped_content.append({
                                "url": url,
                                "error": str(e),
                                "success": False,
                                "scrape_time": scrape_time
                            })
                            
            except (NotImplementedError, OSError, Exception) as crawler_error:
                logger.error(f"💥 Crawl4AI initialization failed: {crawler_error}")
                logger.error(f"   Error type: {type(crawler_error).__name__}")
                logger.warning("🔄 Falling back to basic URL parsing without Crawl4AI")
                
                # Fallback: Use basic HTTP requests when Crawl4AI fails
                scraped_content = await self._fallback_scraping(urls)
                
            # Final scraping summary
            successful_scrapes = len([s for s in scraped_content if s.get('success', False)])
            total_steps = sum(s.get('steps_found', 0) for s in scraped_content if s.get('success', False))
            total_materials = sum(s.get('materials_found', 0) for s in scraped_content if s.get('success', False))
            
            logger.info(f"🎯 Scraping Summary:")
            logger.info(f"   • Successful scrapes: {successful_scrapes}/{len(urls)}")
            logger.info(f"   • Total steps extracted: {total_steps}")
            logger.info(f"   • Total materials found: {total_materials}")
            logger.info(f"   • Success rate: {successful_scrapes/len(urls)*100:.1f}%")
                        
        except Exception as e:
            logger.error(f"💥 Critical error in _scrape_tutorial_content: {e}")
            logger.error(f"   Error type: {type(e).__name__}")
            
        return scraped_content

    def _extract_tutorial_steps(self, content: str) -> List[str]:
        """Extract step-by-step instructions from scraped content"""
        logger.info("🔍 Starting tutorial steps extraction...")
        steps = []
        
        try:
            # Look for common step patterns
            import re
            
            logger.info(f"📝 Processing content of {len(content):,} characters")
            
            # Pattern 1: "Step 1:", "Step 2:", etc.
            logger.info("🔍 Looking for 'Step X:' patterns...")
            step_pattern1 = re.findall(r'Step\s+\d+[:.]\s*([^.!?]*[.!?])', content, re.IGNORECASE)
            logger.info(f"   • Found {len(step_pattern1)} 'Step X:' matches")
            
            # Pattern 2: Numbered lists "1.", "2.", etc.
            logger.info("🔍 Looking for numbered list patterns...")
            step_pattern2 = re.findall(r'^\s*\d+\.\s*([^.!?]*[.!?])', content, re.MULTILINE)
            logger.info(f"   • Found {len(step_pattern2)} numbered list matches")
            
            # Pattern 3: Instructions with action words
            logger.info("🔍 Looking for instruction action words...")
            instruction_words = ['cut', 'glue', 'paint', 'attach', 'remove', 'clean', 'drill', 'fold']
            action_steps = []
            
            for word in instruction_words:
                pattern = re.findall(f'{word}[^.!?]*[.!?]', content, re.IGNORECASE)
                action_steps.extend(pattern[:2])  # Limit to 2 per action word
                if pattern:
                    logger.info(f"   • '{word}': {len(pattern)} matches (kept {min(len(pattern), 2)})")
            
            logger.info(f"   • Total action-based steps: {len(action_steps)}")
            
            # Combine and clean steps
            logger.info("🧹 Combining and cleaning steps...")
            all_steps = step_pattern1 + step_pattern2 + action_steps
            logger.info(f"   • Raw steps before deduplication: {len(all_steps)}")
            
            # Remove duplicates and filter
            unique_steps = []
            seen = set()
            filtered_short = 0
            duplicates = 0
            
            for step in all_steps:
                clean_step = step.strip()
                clean_step_lower = clean_step.lower()
                
                if len(clean_step) <= 10:
                    filtered_short += 1
                    continue
                    
                if clean_step_lower in seen:
                    duplicates += 1
                    continue
                    
                seen.add(clean_step_lower)
                unique_steps.append(clean_step)
            
            logger.info(f"   • Filtered out {filtered_short} short steps (≤10 chars)")
            logger.info(f"   • Removed {duplicates} duplicate steps")
            logger.info(f"   • Final unique steps: {len(unique_steps)}")
            
            # Limit to 8 steps
            final_steps = unique_steps[:8]
            if len(unique_steps) > 8:
                logger.info(f"   • Limited to first 8 steps (had {len(unique_steps)} total)")
            
            # Log first few steps for verification
            for i, step in enumerate(final_steps[:3]):
                logger.info(f"   Step {i+1}: {step[:60]}{'...' if len(step) > 60 else ''}")
            
            if len(final_steps) == 0:
                logger.warning("⚠️ No tutorial steps could be extracted")
            else:
                logger.info(f"✅ Successfully extracted {len(final_steps)} tutorial steps")
            
            return final_steps
            
        except Exception as e:
            logger.error(f"💥 Error extracting tutorial steps: {e}")
            logger.error(f"   Error type: {type(e).__name__}")
            return []

    def _extract_materials_list(self, content: str) -> List[str]:
        """Extract materials list from scraped content"""
        logger.info("🧱 Starting materials extraction...")
        materials = []
        
        try:
            import re
            
            logger.info(f"📝 Processing content of {len(content):,} characters for materials")
            
            # Look for materials section
            logger.info("🔍 Looking for 'materials' section...")
            materials_section = re.search(r'materials?[^:]*:([^.]+)', content, re.IGNORECASE | re.DOTALL)
            materials_found = 0
            
            if materials_section:
                materials_text = materials_section.group(1)
                logger.info(f"   • Found materials section: {len(materials_text)} characters")
                
                # Extract bullet points or listed items
                material_items = re.findall(r'[-•]\s*([^-•\n]+)', materials_text)
                materials_found = len(material_items)
                
                valid_materials = [item.strip() for item in material_items if item.strip()]
                materials.extend(valid_materials)
                
                logger.info(f"   • Extracted {materials_found} material items")
                logger.info(f"   • Valid materials: {len(valid_materials)}")
            else:
                logger.info("   • No 'materials' section found")
            
            # Look for supply lists
            logger.info("🔍 Looking for 'supplies' section...")
            supplies_section = re.search(r'supplies?[^:]*:([^.]+)', content, re.IGNORECASE | re.DOTALL)
            supplies_found = 0
            
            if supplies_section:
                supplies_text = supplies_section.group(1)
                logger.info(f"   • Found supplies section: {len(supplies_text)} characters")
                
                supply_items = re.findall(r'[-•]\s*([^-•\n]+)', supplies_text)
                supplies_found = len(supply_items)
                
                valid_supplies = [item.strip() for item in supply_items if item.strip()]
                materials.extend(valid_supplies)
                
                logger.info(f"   • Extracted {supplies_found} supply items")
                logger.info(f"   • Valid supplies: {len(valid_supplies)}")
            else:
                logger.info("   • No 'supplies' section found")
            
            # Look for additional patterns
            logger.info("🔍 Looking for 'things you need' patterns...")
            need_patterns = [
                r'(?:things|items|stuff)\s+(?:you\s+)?need[^:]*:([^.]+)',
                r'(?:what\s+)?you\s+(?:will\s+)?need[^:]*:([^.]+)',
                r'required\s+(?:items|materials)[^:]*:([^.]+)'
            ]
            
            additional_found = 0
            for pattern in need_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    items = re.findall(r'[-•]\s*([^-•\n]+)', match)
                    valid_items = [item.strip() for item in items if item.strip()]
                    materials.extend(valid_items)
                    additional_found += len(valid_items)
            
            logger.info(f"   • Additional items found: {additional_found}")
            
            # Remove duplicates and clean
            logger.info("🧹 Cleaning and deduplicating materials...")
            
            raw_count = len(materials)
            unique_materials = []
            seen = set()
            duplicates = 0
            
            for material in materials:
                clean_material = material.strip().lower()
                if clean_material and clean_material not in seen and len(clean_material) > 2:
                    seen.add(clean_material)
                    unique_materials.append(material.strip())
                else:
                    duplicates += 1
            
            logger.info(f"   • Raw materials: {raw_count}")
            logger.info(f"   • Duplicates removed: {duplicates}")
            logger.info(f"   • Unique materials: {len(unique_materials)}")
            
            # Limit to 10 materials
            final_materials = unique_materials[:10]
            if len(unique_materials) > 10:
                logger.info(f"   • Limited to first 10 materials (had {len(unique_materials)} total)")
            
            # Log first few materials for verification
            for i, material in enumerate(final_materials[:3]):
                logger.info(f"   Material {i+1}: {material}")
            
            if len(final_materials) == 0:
                logger.warning("⚠️ No materials could be extracted")
            else:
                logger.info(f"✅ Successfully extracted {len(final_materials)} materials")
            
            return final_materials
            
        except Exception as e:
            logger.error(f"💥 Error extracting materials: {e}")
            logger.error(f"   Error type: {type(e).__name__}")
            return []

    async def _fallback_scraping(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Fallback scraping method using basic HTTP requests when Crawl4AI fails
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of basic scraped content
        """
        logger.info("🔄 Using fallback HTTP scraping (no Crawl4AI)")
        scraped_content = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for i, url in enumerate(urls):
                    if not url:
                        continue
                        
                    try:
                        logger.info(f"📄 [{i+1}/{len(urls)}] Fallback scraping: {url}")
                        start_time = time.time()
                        
                        async with session.get(url, timeout=10) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Remove script and style elements
                                for script in soup(["script", "style"]):
                                    script.decompose()
                                
                                # Get clean text
                                text_content = soup.get_text()
                                lines = (line.strip() for line in text_content.splitlines())
                                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                                clean_text = ' '.join(chunk for chunk in chunks if chunk)
                                
                                scrape_time = time.time() - start_time
                                
                                # Basic step and material extraction
                                steps = self._extract_tutorial_steps(clean_text)
                                materials = self._extract_materials_list(clean_text)
                                
                                scraped_content.append({
                                    "url": url,
                                    "title": soup.title.string if soup.title else "",
                                    "content": clean_text[:2000],
                                    "steps": steps,
                                    "materials": materials,
                                    "success": True,
                                    "scrape_time": scrape_time,
                                    "method": "fallback_http",
                                    "steps_found": len(steps),
                                    "materials_found": len(materials)
                                })
                                
                                logger.info(f"✅ Fallback scraping successful for {url}")
                                
                            else:
                                logger.warning(f"❌ HTTP {response.status} for {url}")
                                scraped_content.append({
                                    "url": url,
                                    "error": f"HTTP {response.status}",
                                    "success": False,
                                    "method": "fallback_http"
                                })
                                
                    except Exception as e:
                        logger.error(f"💥 Fallback scraping error for {url}: {e}")
                        scraped_content.append({
                            "url": url,
                            "error": str(e),
                            "success": False,
                            "method": "fallback_http"
                        })
                        
        except Exception as e:
            logger.error(f"💥 Critical error in fallback scraping: {e}")
            
        return scraped_content

    async def _fallback_search(self, queries: List[str]) -> Dict[str, Any]:
        """Fallback search when Tavily is not available"""
        logger.info("Using fallback search (no real web search)")
        
        fallback_results = {}
        for i, query in enumerate(queries[:4]):
            fallback_results[f"query_{i+1}"] = {
                "query": query,
                "answer": f"Fallback: Limited information available for '{query}'. Consider checking manufacturer websites and sustainability databases.",
                "results": []
            }
        
        return fallback_results

    async def get_sustainability_data(self, product_name: str, manufacturer: str = "") -> Dict[str, Any]:
        """
        Get specific sustainability data for a product
        
        Args:
            product_name: Name of the product
            manufacturer: Manufacturer name if available
            
        Returns:
            Dictionary containing sustainability information
        """
        try:
            sustainability_queries = [
                f"{product_name} {manufacturer} sustainability report carbon footprint",
                f"{product_name} environmental impact assessment LCA",
                f"{manufacturer} sustainability certification B-corp carbon neutral",
                f"{product_name} packaging waste recycling environmental impact"
            ]
            
            return await self.search_product_info(sustainability_queries, max_results=2)
            
        except Exception as e:
            logger.error(f"Error getting sustainability data: {e}")
            return {"error": str(e)}
