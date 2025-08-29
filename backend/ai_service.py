import os
import time
import json
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from google import genai as new_genai
from PIL import Image
from config import Config
from prompts import *
from io import BytesIO
import base64
from web_search_service import WebSearchService

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        
        # Initialize both versions of genai client
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        
        # Initialize new genai client for image generation
        self.new_client = new_genai.Client(api_key=Config.GEMINI_API_KEY)
        
        # Initialize web search service
        self.web_search = WebSearchService()
        
        logger.info(f"AI Service initialized with model: {Config.GEMINI_MODEL}")

    async def analyze_product(self, file_path: str) -> Dict[str, Any]:
        """Analyze product from image/video and extract details for environmental assessment with comprehensive logging"""
        logger.info(f"🔍 Starting product analysis for file: {file_path}")
        
        try:
            # For images, we'll use PIL to load and pass directly
            # For videos, we'll need to handle differently
            file_ext = os.path.splitext(file_path)[1].lower()
            logger.info(f"📄 File extension detected: {file_ext}")
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                logger.info("🖼️ Processing as image file...")
                # Handle image files
                image = Image.open(file_path)
                logger.info(f"✅ Image loaded successfully - Size: {image.size}, Mode: {image.mode}")
                
                # Generate product analysis focused on environmental aspects
                logger.info("🤖 Sending to Gemini for product analysis...")
                response = self.model.generate_content([PRODUCT_ANALYSIS_PROMPT, image])
                logger.info("✅ Received response from Gemini")
                
                # Parse the response text to extract JSON
                response_text = response.text.strip()
                logger.info(f"📝 Response length: {len(response_text)} characters")
                logger.debug(f"🔍 Response preview: {response_text[:200]}...")
                
                # Try to extract JSON from the response
                try:
                    # Look for JSON content in the response
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        logger.info("✅ Found JSON structure in response")
                        result = json.loads(json_match.group())
                        logger.info("✅ Successfully parsed JSON response")
                    else:
                        logger.warning("⚠️ No JSON found, using fallback parser")
                        # Fallback: create structure from text response
                        result = self._parse_product_response(response_text)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON parsing failed: {e}")
                    logger.info("🔄 Using fallback response parser")
                    # Fallback parsing
                    result = self._parse_product_response(response_text)
            else:
                logger.warning(f"⚠️ Unsupported file type: {file_ext}")
                # For video files or if upload is needed, we'll use a simplified approach
                # Since video upload API might not be available, we'll treat as image for now
                image = Image.open(file_path) if file_ext in ['.jpg', '.jpeg', '.png'] else None
                if not image:
                    logger.error(f"❌ Cannot process file type: {file_ext}")
                    # If it's a video, extract first frame or use placeholder
                    raise Exception(f"Unsupported file type: {file_ext}. Please use image files.")
                
                response = self.model.generate_content([PRODUCT_ANALYSIS_PROMPT, image])
                
                # Parse the response text to extract JSON
                response_text = response.text.strip()
                
                # Try to extract JSON from the response
                try:
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                    else:
                        result = self._parse_product_response(response_text)
                except json.JSONDecodeError:
                    result = self._parse_product_response(response_text)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in product analysis: {e}")
            raise
    
    def _parse_product_response(self, response_text: str) -> Dict[str, Any]:
        """Parse product analysis response text into structured data"""
        return {
            "product_name": "Unknown Product",
            "product_description": response_text[:200] + "..." if len(response_text) > 200 else response_text,
            "materials": ["Unknown"],
            "manufacturing_location": "Unknown",
            "packaging_info": "Not specified",
            "product_appearance": "As shown in image"
        }

    async def analyze_environmental_impact(self, product_details: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze environmental impact of the product with comprehensive web research and detailed logging"""
        logger.info(f"🌱 Starting environmental impact analysis for: {product_details.get('product_name', 'Unknown Product')}")
        
        try:
            # Generate search queries for environmental research
            logger.info("🔍 Step 1: Generating search queries for environmental research...")
            search_queries = await self._generate_search_queries(product_details)
            logger.info(f"✅ Generated {len(search_queries)} search queries: {search_queries}")
            
            # Perform comprehensive web search using Tavily
            logger.info("🌐 Step 2: Performing comprehensive web search using Tavily...")
            web_search_results = await self.web_search.search_product_info(search_queries)
            logger.info(f"✅ Web search completed with {len(web_search_results)} query results")
            
            # Log search results summary
            for query_key, query_result in web_search_results.items():
                if isinstance(query_result, dict):
                    logger.debug(f"   🔍 {query_key}: {query_result.get('query', 'Unknown query')}")
                    logger.debug(f"      💡 Answer length: {len(query_result.get('answer', ''))} chars")
                    logger.debug(f"      📄 Results count: {len(query_result.get('results', []))}")
            
            # Get additional sustainability data
            logger.info("📊 Step 3: Getting additional sustainability data...")
            sustainability_data = await self.web_search.get_sustainability_data(
                product_details.get("product_name", ""),
                product_details.get("manufacturer", "")
            )
            logger.info(f"✅ Sustainability data retrieved with {len(sustainability_data)} data points")
            
            # Format web context for LLM
            logger.info("📝 Step 4: Formatting web context for LLM analysis...")
            web_context = self._format_web_context(web_search_results, sustainability_data)
            logger.info(f"✅ Web context formatted - Length: {len(web_context)} characters")
            logger.debug(f"🔍 Web context preview: {web_context[:300]}...")
            
            # Analyze environmental impact with comprehensive web context
            logger.info("🤖 Step 5: Sending to Gemini for environmental impact analysis...")
            prompt = ENVIRONMENTAL_ANALYSIS_PROMPT.render(
                product_name=product_details.get("product_name", ""),
                product_description=product_details.get("product_description", ""),
                materials=", ".join(product_details.get("materials", [])),
                manufacturing_location=product_details.get("manufacturing_location", "Unknown"),
                packaging_info=product_details.get("packaging_info", ""),
                web_context=web_context
            )
            logger.debug(f"📝 Prompt length: {len(prompt)} characters")
            
            response = self.model.generate_content(prompt)
            logger.info("✅ Received environmental analysis response from Gemini")
            
            # Parse response
            response_text = response.text.strip()
            logger.info(f"📝 Environmental analysis response length: {len(response_text)} characters")
            logger.debug(f"🔍 Response preview: {response_text[:300]}...")
            
            try:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    logger.info("✅ Found JSON structure in environmental analysis")
                    result = json.loads(json_match.group())
                    logger.info("✅ Successfully parsed environmental analysis JSON")
                else:
                    logger.warning("⚠️ No JSON found in environmental analysis, using fallback parser")
                    result = self._parse_environmental_response(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Environmental analysis JSON parsing failed: {e}")
                logger.info("🔄 Using fallback environmental response parser")
                result = self._parse_environmental_response(response_text)
            
            # Log analysis results summary
            logger.info("📊 Environmental Analysis Results Summary:")
            logger.info(f"   🎯 Sustainability Score: {result.get('sustainability_score', 'N/A')}/10")
            logger.info(f"   ✅ Positive Aspects: {len(result.get('positive_aspects', []))} items")
            logger.info(f"   ❌ Negative Aspects: {len(result.get('negative_aspects', []))} items")
            logger.info(f"   🔄 Alternatives: {len(result.get('alternatives', []))} suggestions")
            
            logger.info("🌱 Environmental impact analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"💥 Error in environmental impact analysis: {str(e)}", exc_info=True)
            raise
    
    def _parse_environmental_response(self, response_text: str) -> Dict[str, Any]:
        """Parse environmental analysis response text into structured data"""
        return {
            "positive_aspects": ["Eco-friendly materials", "Sustainable packaging", "Local manufacturing"],
            "negative_aspects": ["High carbon footprint", "Non-recyclable components", "Excessive packaging"],
            "alternatives": ["Local alternatives", "Eco-friendly brands", "Second-hand options"],
            "sustainability_score": 5
        }

    async def _generate_search_queries(self, product_details: Dict[str, Any]) -> List[str]:
        try:
            prompt = SEARCH_QUERIES_PROMPT.render(
                product_name=product_details.get("product_name", ""),
                product_description=product_details.get("product_description", ""),
                materials=", ".join(product_details.get("materials", [])),
                manufacturing_location=product_details.get("manufacturing_location", "Unknown")
            )
            
            response = self.model.generate_content(prompt)
            queries_text = response.text.strip()
            
            try:
                import ast
                queries = ast.literal_eval(queries_text)
                return queries if isinstance(queries, list) else []
            except:
                # Fallback: split by lines and clean up
                lines = queries_text.split('\n')
                queries = [line.strip('- "\'') for line in lines if line.strip() and not line.strip().startswith('[')]
                return queries[:4]  # Limit to 4 queries
                
        except Exception as e:
            logger.error(f"Error generating search queries: {e}")
            return []

    async def _get_web_context(self, search_queries: List[str]) -> str:
      
        context_parts = []
        for query in search_queries:
            context_parts.append(f"Search for '{query}': [Web search results would be integrated here]")
        
        return "\n".join(context_parts)

    async def generate_environmental_recommendation(self, product_details: Dict[str, Any], env_analysis: Dict[str, Any]) -> str:
        """Generate overall environmental recommendation"""
        try:
            prompt = ENVIRONMENTAL_RECOMMENDATION_PROMPT.render(
                product_name=product_details.get("product_name", ""),
                sustainability_score=env_analysis.get("sustainability_score", 0),
                positive_aspects=", ".join(env_analysis.get("positive_aspects", [])),
                negative_aspects=", ".join(env_analysis.get("negative_aspects", [])),
                alternatives=", ".join(env_analysis.get("alternatives", []))
            )
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return "Unable to generate recommendation at this time."

    async def generate_diy_projects(self, file_path: str) -> Dict[str, Any]:
        """Generate enhanced DIY project ideas using web scraping for real tutorials"""
        try:
            # Handle image files directly with PIL
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                raise Exception(f"Unsupported file type: {file_ext}. Please use image files.")
            
            # First, analyze the product to understand what it is
            image = Image.open(file_path)
            
            # Quick product identification
            product_identification = self.model.generate_content([
                "Identify this product in 1-2 words and list its main materials. Format: Product: [name], Materials: [material1, material2]",
                image
            ])
            
            product_info = product_identification.text.strip()
            logger.info(f"Product identified: {product_info}")
            
            # Extract product name and materials
            product_name = "unknown item"
            materials = ["plastic", "metal"]
            
            try:
                if "Product:" in product_info:
                    parts = product_info.split("Materials:")
                    product_name = parts[0].replace("Product:", "").strip()
                    if len(parts) > 1:
                        materials_str = parts[1].strip()
                        materials = [m.strip() for m in materials_str.split(",")]
            except:
                pass
            
            # Search for real DIY tutorials online
            logger.info(f"🔍 Step 6: Searching for DIY tutorials for product: {product_name}")
            logger.info(f"📦 Using materials: {materials}")
            
            search_start_time = time.time()
            diy_tutorials = await self.web_search.scrape_diy_tutorials(product_name, materials)
            search_duration = time.time() - search_start_time
            
            logger.info(f"🌐 DIY tutorial search completed in {search_duration:.2f}s")
            logger.info(f"📚 Found {len(diy_tutorials)} tutorial sources")
            
            # Log tutorial sources found
            for i, tutorial in enumerate(diy_tutorials[:3]):  # Log first 3
                if tutorial.get('success', False):
                    logger.info(f"   📄 Tutorial {i+1}: {tutorial.get('title', 'No title')}")
                    logger.info(f"      🔗 URL: {tutorial.get('url', '')}")
                    logger.info(f"      📋 Steps: {tutorial.get('steps_found', 0)}")
                    logger.info(f"      🛠️ Materials: {tutorial.get('materials_found', 0)}")
                else:
                    logger.warning(f"   ❌ Tutorial {i+1} failed: {tutorial.get('error', 'Unknown error')}")
            
            if len(diy_tutorials) > 3:
                logger.info(f"   ... and {len(diy_tutorials) - 3} more tutorials")
                
            # Count successful tutorials
            successful_tutorials = len([t for t in diy_tutorials if t.get('success', False)])
            logger.info(f"✅ Successfully scraped {successful_tutorials}/{len(diy_tutorials)} tutorials")
            
            # Create enhanced prompt with web-scraped tutorial data
            enhanced_prompt = self._create_enhanced_diy_prompt(product_name, materials, diy_tutorials)
            
            # Generate DIY projects with enhanced context
            response = self.model.generate_content([enhanced_prompt, image])
            
            # Parse response
            response_text = response.text.strip()
            try:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = self._parse_diy_response(response_text)
            except json.JSONDecodeError:
                result = self._parse_diy_response(response_text)
            
            # Enhance image generation prompts with real tutorial insights
            for difficulty in ['easy', 'medium', 'hard']:
                if difficulty in result:
                    # Enhance the image generation prompt with context from scraped tutorials
                    if 'image_generation_prompt' in result[difficulty]:
                        enhanced_image_prompt = self._enhance_image_prompt(
                            result[difficulty]['image_generation_prompt'],
                            diy_tutorials,
                            product_name
                        )
                        
                        project_name = result[difficulty].get('project_name', f'{difficulty}_project').replace(' ', '_')
                        
                        # Generate image with enhanced prompt
                        img_base64, img_filename = self.generate_product_image(enhanced_image_prompt, f"{difficulty}_{project_name}")
                        
                        if img_base64 and img_filename:
                            result[difficulty]['generated_image'] = {
                                'base64': img_base64,
                                'filename': img_filename,
                                'url': f"/static/generated_images/{img_filename}"
                            }
                            logger.info(f"Generated enhanced image for {difficulty} project")
                        else:
                            logger.warning(f"Failed to generate image for {difficulty} project")
            
            # Add tutorial sources to result
            result['tutorial_sources'] = self._extract_tutorial_sources(diy_tutorials)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in enhanced DIY analysis: {e}")
            # Fallback to basic analysis
            try:
                return await self._generate_basic_diy_projects(file_path)
            except:
                raise e
    
    def _parse_diy_response(self, response_text: str) -> Dict[str, Any]:
        """Parse DIY analysis response text into structured data"""
        return {
            "easy": {
                "project_name": "Simple Upcycle Project",
                "difficulty_level": "Easy",
                "materials_required": [{"material": "Basic tools", "quantity": "1 set"}],
                "steps": [
                    {"step_number": 1, "description": "Clean the item", "estimated_time": "5 minutes", "safety_tips": "Wear gloves"},
                    {"step_number": 2, "description": "Modify as needed", "estimated_time": "10 minutes", "safety_tips": "Use tools carefully"},
                    {"step_number": 3, "description": "Finish the project", "estimated_time": "5 minutes", "safety_tips": "Check all connections"}
                ],
                "estimated_time": "20 minutes",
                "safety_tips": ["Wear protective gear", "Work in well-ventilated area"],
                "image_description": "A simple upcycled item with basic modifications",
                "image_generation_prompt": "A photo of a simple, clean upcycled household item with basic modifications, shown on a plain white background"
            },
            "medium": {
                "project_name": "Intermediate Upcycle Project",
                "difficulty_level": "Medium",
                "materials_required": [{"material": "Additional tools", "quantity": "1 set"}],
                "steps": [
                    {"step_number": 1, "description": "Prepare materials", "estimated_time": "10 minutes", "safety_tips": "Organize workspace"},
                    {"step_number": 2, "description": "Cut and shape", "estimated_time": "20 minutes", "safety_tips": "Use cutting tools safely"},
                    {"step_number": 3, "description": "Assemble parts", "estimated_time": "15 minutes", "safety_tips": "Check fit before final assembly"},
                    {"step_number": 4, "description": "Add finishing touches", "estimated_time": "10 minutes", "safety_tips": "Allow proper drying time"},
                    {"step_number": 5, "description": "Final inspection", "estimated_time": "5 minutes", "safety_tips": "Test functionality"}
                ],
                "estimated_time": "60 minutes",
                "safety_tips": ["Use proper tools", "Take breaks", "Keep workspace clean"],
                "image_description": "A more complex upcycled item with multiple modifications",
                "image_generation_prompt": "A photo of a creatively upcycled item with intermediate-level craftsmanship, showing multiple colors and materials, displayed in a well-lit environment"
            },
            "hard": {
                "project_name": "Advanced Upcycle Project",
                "difficulty_level": "Hard",
                "materials_required": [{"material": "Professional tools", "quantity": "1 set"}],
                "steps": [
                    {"step_number": 1, "description": "Plan the project", "estimated_time": "15 minutes", "safety_tips": "Measure twice, cut once"},
                    {"step_number": 2, "description": "Prepare advanced materials", "estimated_time": "20 minutes", "safety_tips": "Check material compatibility"},
                    {"step_number": 3, "description": "Execute complex cuts", "estimated_time": "30 minutes", "safety_tips": "Use proper cutting techniques"},
                    {"step_number": 4, "description": "Assembly with precision", "estimated_time": "25 minutes", "safety_tips": "Follow assembly sequence"},
                    {"step_number": 5, "description": "Add advanced features", "estimated_time": "20 minutes", "safety_tips": "Test each feature"},
                    {"step_number": 6, "description": "Professional finishing", "estimated_time": "15 minutes", "safety_tips": "Use appropriate finishing materials"},
                    {"step_number": 7, "description": "Quality control", "estimated_time": "10 minutes", "safety_tips": "Perform thorough inspection"}
                ],
                "estimated_time": "135 minutes",
                "safety_tips": ["Professional expertise recommended", "Use high-quality tools", "Follow safety protocols"],
                "image_description": "A sophisticated upcycled item with professional-grade modifications",
                "image_generation_prompt": "A photo of an expertly crafted upcycled item showing advanced techniques, premium materials, and professional-quality finishing, displayed in a showroom setting"
            }
        }

    def generate_product_image(self, prompt: str, project_name: str = "generated_project") -> tuple[str, str]:
        """
        Generate an image of the final DIY product using Gemini's image generation model
        
        Args:
            prompt: Text description of the image to generate
            project_name: Name for saving the generated image
            
        Returns:
            tuple: (base64_image_data, image_filename)
        """
        try:
            logger.info(f"Generating image for: {project_name}")
            
            # Use the new genai client for image generation
            response = self.new_client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[prompt]
            )
            
            # Extract image from response
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    # Convert to PIL Image
                    image = Image.open(BytesIO(part.inline_data.data))
                    
                    # Save image to static directory
                    os.makedirs("static/generated_images", exist_ok=True)
                    timestamp = int(time.time())
                    filename = f"{project_name}_{timestamp}.png"
                    filepath = f"static/generated_images/{filename}"
                    image.save(filepath)
                    
                    # Convert to base64 for API response
                    img_buffer = BytesIO()
                    image.save(img_buffer, format='PNG')
                    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                    
                    logger.info(f"Image generated successfully: {filename}")
                    return img_base64, filename
            
            logger.warning("No image found in response")
            return None, None
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None, None

    def _format_web_context(self, web_search_results: Dict[str, Any], sustainability_data: Dict[str, Any]) -> str:
        """Format web search results for LLM context"""
        context_parts = []
        
        try:
            # Add web search results
            for query_key, query_data in web_search_results.items():
                if isinstance(query_data, dict) and 'answer' in query_data:
                    context_parts.append(f"Query: {query_data.get('query', '')}")
                    context_parts.append(f"Answer: {query_data.get('answer', '')}")
                    
                    # Add results if available
                    for result in query_data.get('results', [])[:2]:  # Limit to 2 results per query
                        if 'content' in result:
                            context_parts.append(f"Source: {result.get('title', 'Unknown')}")
                            context_parts.append(f"Content: {result.get('content', '')[:300]}...")
                    context_parts.append("---")
            
            # Add sustainability data
            context_parts.append("\nSUSTAINABILITY DATA:")
            for query_key, query_data in sustainability_data.items():
                if isinstance(query_data, dict) and 'answer' in query_data:
                    context_parts.append(f"Sustainability Query: {query_data.get('query', '')}")
                    context_parts.append(f"Findings: {query_data.get('answer', '')}")
            
            formatted_context = "\n".join(context_parts)
            return formatted_context[:4000]  # Limit context size
            
        except Exception as e:
            logger.error(f"Error formatting web context: {e}")
            return "Web context temporarily unavailable"

    def _create_enhanced_diy_prompt(self, product_name: str, materials: List[str], diy_tutorials: Dict[str, Any]) -> str:
        """Create enhanced DIY prompt using scraped tutorial data"""
        tutorial_context = ""
        
        try:
            # Extract useful information from scraped tutorials
            tutorial_insights = []
            
            for tutorial_key, tutorial_data in diy_tutorials.items():
                if 'scraped_tutorials' in tutorial_data:
                    for tutorial in tutorial_data['scraped_tutorials']:
                        if tutorial.get('success', False):
                            if tutorial.get('steps'):
                                tutorial_insights.append(f"Tutorial steps found: {'; '.join(tutorial['steps'][:3])}")
                            if tutorial.get('materials'):
                                tutorial_insights.append(f"Materials used: {', '.join(tutorial['materials'][:5])}")
            
            if tutorial_insights:
                tutorial_context = f"Real tutorial insights for {product_name}:\n" + "\n".join(tutorial_insights[:5])
                
        except Exception as e:
            logger.error(f"Error creating enhanced DIY prompt: {e}")
        
        enhanced_prompt = f"""
You are an expert DIY Upcycling Consultant with access to real online tutorial data. 
Based on the {product_name} shown in the image and the following real-world tutorial insights, create 3 comprehensive DIY project ideas.

{tutorial_context}

Product: {product_name}
Materials: {', '.join(materials)}

Create projects that incorporate techniques and ideas from real tutorials while being practical and environmentally focused.

Please provide your response as a JSON object in this exact format:
{{
  "easy": {{
    "project_name": "Simple project name",
    "difficulty_level": "Easy",
    "materials_required": [{{"material": "Item name", "quantity": "Amount"}}],
    "steps": [
      {{
        "step_number": 1,
        "description": "Detailed step description based on real tutorial methods", 
        "estimated_time": "Time",
        "safety_tips": "Safety advice"
      }}
    ],
    "estimated_time": "Total time",
    "safety_tips": ["tip1", "tip2"],
    "image_description": "Description of final product",
    "image_generation_prompt": "Highly detailed visual description for AI image generation of the finished project, including specific colors, textures, materials, lighting, and setting"
  }},
  "medium": {{
    // Same structure with 5-6 steps incorporating advanced techniques from tutorials
  }},
  "hard": {{
    // Same structure with 7+ steps using professional techniques found in tutorials
  }}
}}

Focus on:
- Incorporating actual techniques found in real tutorials
- Using materials that are commonly available
- Creating visually appealing and functional end products
- Providing extremely detailed image generation prompts for realistic final product visualization
"""
        
        return enhanced_prompt

    def _enhance_image_prompt(self, base_prompt: str, diy_tutorials: Dict[str, Any], product_name: str) -> str:
        """Enhance image generation prompt with insights from scraped tutorials"""
        try:
            # Extract visual details from scraped tutorials
            visual_details = []
            
            for tutorial_key, tutorial_data in diy_tutorials.items():
                if 'scraped_tutorials' in tutorial_data:
                    for tutorial in tutorial_data['scraped_tutorials']:
                        if tutorial.get('success', False) and tutorial.get('content'):
                            content = tutorial['content'].lower()
                            
                            # Look for color mentions
                            colors = ['red', 'blue', 'green', 'yellow', 'white', 'black', 'brown', 'purple', 'orange', 'pink']
                            for color in colors:
                                if color in content:
                                    visual_details.append(f"with {color} accents")
                                    break
                            
                            # Look for finish descriptions
                            finishes = ['glossy', 'matte', 'rustic', 'modern', 'vintage', 'polished', 'painted']
                            for finish in finishes:
                                if finish in content:
                                    visual_details.append(f"featuring {finish} finish")
                                    break
            
            # Enhance the base prompt
            enhancement = ""
            if visual_details:
                enhancement = f", {', '.join(visual_details[:2])}"
            
            enhanced_prompt = f"{base_prompt}{enhancement}, photographed in natural lighting with a clean, professional background, showing fine details and textures, high quality product photography style"
            
            return enhanced_prompt[:500]  # Limit prompt length
            
        except Exception as e:
            logger.error(f"Error enhancing image prompt: {e}")
            return base_prompt

    def _extract_tutorial_sources(self, diy_tutorials: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract tutorial source information"""
        sources = []
        
        try:
            for tutorial_key, tutorial_data in diy_tutorials.items():
                if 'scraped_tutorials' in tutorial_data:
                    for tutorial in tutorial_data['scraped_tutorials']:
                        if tutorial.get('success', False):
                            sources.append({
                                'title': tutorial.get('title', 'DIY Tutorial'),
                                'url': tutorial.get('url', ''),
                                'type': 'Tutorial'
                            })
                        
                if len(sources) >= 5:  # Limit to 5 sources
                    break
                    
        except Exception as e:
            logger.error(f"Error extracting tutorial sources: {e}")
        
        return sources

    async def _generate_basic_diy_projects(self, file_path: str) -> Dict[str, Any]:
        """Fallback method for basic DIY project generation"""
        try:
            image = Image.open(file_path)
            response = self.model.generate_content([DIY_ANALYSIS_PROMPT, image])
            
            response_text = response.text.strip()
            try:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = self._parse_diy_response(response_text)
            except json.JSONDecodeError:
                result = self._parse_diy_response(response_text)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in basic DIY generation: {e}")
            return self._parse_diy_response("")
