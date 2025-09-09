# EcoMatrix Backend Setup Guide

## Enhanced Features
- **Real Web Search**: Uses Tavily API for comprehensive environmental data
- **Tutorial Scraping**: Crawl4AI scrapes real DIY tutorials from the web  
- **AI Image Generation**: Gemini 2.5 Flash generates final product images
- **Environmental Analysis**: Comprehensive sustainability assessments

## Installation

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **API Keys Required**

Get your API keys from:
- **Gemini API**: https://makersuite.google.com/app/apikey
- **Tavily API**: https://tavily.com/ (Sign up for free tier)

3. **Environment Setup**
```bash
cp .env.sample .env
```

Edit `.env` and add your API keys:
```env
GEMINI_API_KEY=your_actual_gemini_key
TAVILY_API_KEY=your_actual_tavily_key
```

## Features

### 🔍 Enhanced Product Analysis
- Real-time web search for environmental data
- Carbon footprint analysis from multiple sources
- Sustainability certifications lookup
- Manufacturing practice research

### 🔨 Advanced DIY Projects  
- Scrapes real tutorials from DIY websites
- Extracts actual step-by-step instructions
- Incorporates real material lists from tutorials
- Generates enhanced visual prompts from tutorial insights

### 🖼️ AI Image Generation
- Creates realistic final product images
- Enhanced prompts based on scraped tutorial data
- Professional photography-style rendering
- Visual previews for each difficulty level

## Usage

1. **Start Server**
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Test Enhanced Features**
```bash
python test_enhanced.py
```

## How It Works

### Environmental Analysis Flow:
1. **Product Identification** → Extract product details from image
2. **Web Search** → Tavily searches for environmental data
3. **Data Scraping** → Additional sustainability research  
4. **AI Analysis** → Comprehensive environmental assessment
5. **Recommendation** → Actionable sustainability advice

### DIY Project Flow:
1. **Product Recognition** → Identify item and materials
2. **Tutorial Search** → Tavily finds relevant DIY tutorials
3. **Content Scraping** → Crawl4AI extracts tutorial details
4. **Enhanced Generation** → AI creates projects using real tutorial data
5. **Image Creation** → Generate realistic final product images

## API Endpoints

- `POST /analyze-product` - Enhanced environmental analysis
- `POST /analyze-diy` - Advanced DIY projects with images
- `GET /health` - Service health check

## Expected Output

### Product Analysis:
```json
{
  "product_name": "Identified product",
  "environmental_analysis": {
    "sustainability_score": 7,
    "positive_aspects": ["Real data points"],
    "negative_aspects": ["Actual concerns found"],
    "alternatives": ["Research-backed alternatives"]
  },
  "web_sources": ["List of researched sources"]
}
```

### DIY Projects:
```json
{
  "projects": {
    "easy": {
      "project_name": "Tutorial-inspired project",
      "steps": ["Real tutorial techniques"],
      "generated_image": {
        "url": "/static/generated_images/project.png",
        "base64": "image_data"
      }
    }
  },
  "tutorial_sources": ["Scraped tutorial URLs"]
}
```

## Troubleshooting

### No Web Search Results
- Check Tavily API key is valid
- Verify internet connection
- Check API rate limits

### Image Generation Issues
- Ensure Gemini API key has image generation access
- Check if model supports image generation
- Verify sufficient API quota

### Crawling Errors
- Some websites may block crawlers
- Rate limiting may cause delays
- Fallback to basic analysis if scraping fails

## Performance Notes

- Web searches add 5-10 seconds per request
- Tutorial scraping can take 10-20 seconds  
- Image generation adds 3-8 seconds
- Total enhanced analysis: 20-40 seconds per request

The enhanced features provide significantly more accurate and comprehensive results but require additional processing time.
