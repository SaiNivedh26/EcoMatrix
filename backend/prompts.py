from jinja2 import Template

# Product Analysis Prompts - Focus on Environmental Sustainability
PRODUCT_ANALYSIS_PROMPT = """
You are a professional Product Analyzer focused on environmental sustainability. 
Analyze the product in the provided image and extract information in JSON format.

Please provide your response as a JSON object with these fields:
{
  "product_name": "Name of the product",
  "product_description": "Detailed description of the product",
  "materials": ["material1", "material2"],
  "manufacturing_location": "Location if visible",
  "packaging_info": "Description of packaging",
  "product_appearance": "Visual description"
}

Focus on information relevant to environmental impact assessment.
"""

ENVIRONMENTAL_ANALYSIS_PROMPT = Template("""
You are an Environmental Sustainability Expert. Based on the following product information, provide a comprehensive sustainability analysis:

Product Details:
- Name: {{ product_name }}
- Description: {{ product_description }}
- Materials/Ingredients: {{ materials }}
- Manufacturing Location: {{ manufacturing_location }}
- Packaging: {{ packaging_info }}

Web Research Context:
{{ web_context }}

Provide detailed analysis on:

1. POSITIVE ENVIRONMENTAL ASPECTS (at least 3 points):
   - What makes this product environmentally friendly
   - Sustainable practices or materials used
   - Positive environmental impact

2. NEGATIVE ENVIRONMENTAL ASPECTS (at least 3 points):
   - Environmental concerns or damages
   - Unsustainable practices
   - Carbon footprint issues

3. SUSTAINABLE ALTERNATIVES (at least 3 suggestions):
   - Better eco-friendly alternatives
   - Local or low-impact options
   - DIY alternatives

4. SUSTAINABILITY SCORE: Rate 1-10 (10 being most sustainable)

Consider factors like:
- Carbon footprint and transportation
- Packaging materials and waste
- Manufacturing processes and energy use
- Recyclability and end-of-life impact
- Local vs imported sourcing
- Renewable vs non-renewable materials
""")

DIY_ANALYSIS_PROMPT = """
You are a Creative DIY Upcycling Expert focused on environmental sustainability. 
Based on the item shown in the image, create 3 DIY project ideas with different difficulty levels.

Please provide your response as a JSON object in this exact format:

{
  "easy": {
    "project_name": "Simple project name",
    "difficulty_level": "Easy",
    "materials_required": [{"material": "Item name", "quantity": "Amount"}],
    "steps": [
      {
        "step_number": 1,
        "description": "Step description", 
        "estimated_time": "Time",
        "safety_tips": "Safety advice"
      }
    ],
    "estimated_time": "Total time",
    "safety_tips": ["tip1", "tip2"],
    "image_description": "Description of final product",
    "image_generation_prompt": "Detailed visual description for AI image generation of the finished project, including colors, materials, shape, and setting"
  },
  "medium": {
    // Same structure with 5-6 steps
  },
  "hard": {
    // Same structure with 7+ steps
  }
}

Focus on:
- Extending product life through creative reuse
- Reducing waste and environmental impact
- Creating practical and beautiful upcycled items
- Using minimal additional materials
- Providing detailed visual descriptions for image generation
"""

SEARCH_QUERIES_PROMPT = Template("""
You are an environmental research query generator. Based on this product information, create 4 specific web search queries to find current information about:

1. Environmental impact and carbon footprint data
2. Manufacturing sustainability practices and certifications
3. Packaging waste and recycling information  
4. Sustainable alternatives and eco-friendly competitors

Product: {{ product_name }}
Description: {{ product_description }}
Materials: {{ materials }}
Manufacturing Location: {{ manufacturing_location }}

Return only a Python list of 4 search query strings focused on environmental sustainability.
""")

ENVIRONMENTAL_RECOMMENDATION_PROMPT = Template("""
Based on the comprehensive environmental analysis, provide an overall sustainability recommendation:

Product: {{ product_name }}
Sustainability Score: {{ sustainability_score }}/10
Environmental Benefits: {{ positive_aspects }}
Environmental Concerns: {{ negative_aspects }}
Available Alternatives: {{ alternatives }}

Provide a clear, actionable recommendation (2-3 sentences) on whether environmentally-conscious consumers should:
- Choose this product (if sustainability score >= 7)
- Look for better alternatives (if score 4-6)
- Avoid this product entirely (if score <= 3)

Include the main environmental reason for your recommendation and one specific alternative if suggesting to avoid.
""")

WEB_SEARCH_CONTEXT_PROMPT = """
Based on the following web search results about the product, extract and summarize key environmental sustainability information:

Focus on:
- Carbon footprint data
- Sustainable manufacturing practices
- Environmental certifications
- Packaging and waste impact
- Company sustainability initiatives

Ignore irrelevant information and focus only on environmental aspects.
"""
