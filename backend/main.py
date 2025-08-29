import logging
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
from typing import Dict, Any, List
from pathlib import Path
import os
import sys

from config import Config
from ai_service import AIService
from file_service import FileService

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Services
ai_service = None
file_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global ai_service, file_service
    try:
        ai_service = AIService()
        file_service = FileService()
        logger.info("✅ EcoMatrix Backend Services Initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 EcoMatrix Backend Shutting Down")

# FastAPI app
app = FastAPI(
    title="EcoMatrix API",
    description="AI-powered sustainability and DIY analysis platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = ["uploads", "temp", "static", "static/uploads", "static/generated_images"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Ensure directories exist
ensure_directories()

# Serve static files (for the simple UI)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the simple test UI"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EcoMatrix - Sustainability Analysis</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
            .header p { font-size: 1.1rem; opacity: 0.9; }
            .content { padding: 40px; }
            .tab-buttons {
                display: flex;
                margin-bottom: 30px;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            .tab-button {
                flex: 1;
                padding: 15px 20px;
                border: none;
                background: #f5f5f5;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 1rem;
                font-weight: 600;
            }
            .tab-button.active {
                background: #4CAF50;
                color: white;
            }
            .tab-button:hover:not(.active) {
                background: #e8e8e8;
            }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            .upload-area {
                border: 3px dashed #4CAF50;
                border-radius: 15px;
                padding: 40px;
                text-align: center;
                margin-bottom: 20px;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .upload-area:hover { 
                border-color: #45a049; 
                background: #f9fff9;
            }
            .upload-area.dragover {
                border-color: #45a049;
                background: #f0fff0;
            }
            input[type="file"] { display: none; }
            .btn {
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1rem;
                font-weight: 600;
                transition: all 0.3s ease;
                width: 100%;
                margin-top: 20px;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
            }
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
            }
            .form-group textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 1rem;
                resize: vertical;
                transition: border-color 0.3s ease;
            }
            .form-group textarea:focus {
                outline: none;
                border-color: #4CAF50;
            }
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #4CAF50;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .result {
                display: none;
                margin-top: 30px;
                padding: 25px;
                background: #f8f9fa;
                border-radius: 10px;
                border-left: 5px solid #4CAF50;
            }
            .result-section {
                margin-bottom: 25px;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }
            .result-section h3 {
                color: #4CAF50;
                margin-bottom: 15px;
                font-size: 1.3rem;
            }
            .result-list {
                list-style: none;
                padding: 0;
            }
            .result-list li {
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }
            .result-list li:last-child {
                border-bottom: none;
            }
            .score {
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                color: white;
                font-weight: bold;
                margin-left: 10px;
            }
            .score.high { background: #4CAF50; }
            .score.medium { background: #ff9800; }
            .score.low { background: #f44336; }
            .diy-project {
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            .diy-project:hover {
                transform: translateY(-5px);
            }
            .difficulty {
                display: inline-block;
                padding: 5px 12px;
                border-radius: 15px;
                font-size: 0.9rem;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .difficulty.easy { background: #4CAF50; color: white; }
            .difficulty.medium { background: #ff9800; color: white; }
            .difficulty.hard { background: #f44336; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌱 EcoMatrix</h1>
                <p>AI-Powered Sustainability & DIY Analysis</p>
            </div>
            
            <div class="content">
                <div class="tab-buttons">
                    <button class="tab-button active" onclick="switchTab('product')">
                        🛍️ Product Analysis
                    </button>
                    <button class="tab-button" onclick="switchTab('diy')">
                        🔨 DIY Projects
                    </button>
                </div>

                <!-- Product Analysis Tab -->
                <div id="product-tab" class="tab-content active">
                    <form id="product-form">
                        <div class="upload-area" onclick="document.getElementById('product-file').click()">
                            <h3>📸 Upload Product Image/Video</h3>
                            <p>Click here or drag & drop your file</p>
                            <input type="file" id="product-file" name="file" accept="image/*,video/*" required>
                        </div>
                        
                        <button type="submit" class="btn">Analyze Product</button>
                    </form>
                </div>

                <!-- DIY Projects Tab -->
                <div id="diy-tab" class="tab-content">
                    <form id="diy-form">
                        <div class="upload-area" onclick="document.getElementById('diy-file').click()">
                            <h3>📦 Upload Item for DIY Ideas</h3>
                            <p>Click here or drag & drop your file</p>
                            <input type="file" id="diy-file" name="file" accept="image/*,video/*" required>
                        </div>
                        
                        <button type="submit" class="btn">Generate DIY Projects</button>
                    </form>
                </div>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Analyzing with AI... This may take a moment.</p>
                </div>

                <div class="result" id="result"></div>
            </div>
        </div>

        <script>
            function switchTab(tabName) {
                // Remove active class from all tabs
                document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                
                // Add active class to selected tab
                event.target.classList.add('active');
                document.getElementById(tabName + '-tab').classList.add('active');
                
                // Clear any previous results
                document.getElementById('result').style.display = 'none';
                document.getElementById('result').innerHTML = '';
            }

            // Handle file upload display
            document.getElementById('product-file').addEventListener('change', function() {
                const fileName = this.files[0]?.name;
                if (fileName) {
                    const uploadArea = this.parentElement;
                    const existingText = uploadArea.querySelector('p');
                    if (existingText) {
                        existingText.innerHTML = `✅ Selected: ${fileName}`;
                        uploadArea.querySelector('h3').innerHTML = '📸 File Selected';
                    }
                }
            });

            document.getElementById('diy-file').addEventListener('change', function() {
                const fileName = this.files[0]?.name;
                if (fileName) {
                    const uploadArea = this.parentElement;
                    const existingText = uploadArea.querySelector('p');
                    if (existingText) {
                        existingText.innerHTML = `✅ Selected: ${fileName}`;
                        uploadArea.querySelector('h3').innerHTML = '🔨 File Selected';
                    }
                }
            });

            // Product Analysis Form
            document.getElementById('product-form').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData();
                const file = document.getElementById('product-file').files[0];
                
                if (!file) {
                    alert('Please select a file first!');
                    return;
                }
                
                formData.append('file', file);
                
                showLoading();
                
                try {
                    const response = await fetch('/analyze-product', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const result = await response.json();
                    displayProductResult(result);
                } catch (error) {
                    console.error('Error:', error);
                    hideLoading();
                    alert('Error analyzing product: ' + error.message);
                }
            });

            // DIY Form
            document.getElementById('diy-form').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData();
                const file = document.getElementById('diy-file').files[0];
                
                if (!file) {
                    alert('Please select a file first!');
                    return;
                }
                
                formData.append('file', file);
                
                showLoading();
                
                try {
                    const response = await fetch('/analyze-diy', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const result = await response.json();
                    displayDIYResult(result);
                } catch (error) {
                    console.error('Error:', error);
                    hideLoading();
                    alert('Error generating DIY projects: ' + error.message);
                }
            });

            function showLoading() {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';
            }

            function hideLoading() {
                document.getElementById('loading').style.display = 'none';
            }

            function getScoreClass(score) {
                if (score >= 7) return 'high';
                if (score >= 4) return 'medium';
                return 'low';
            }

            function displayProductResult(data) {
                hideLoading();
                
                const resultDiv = document.getElementById('result');
                const product = data.product_details;
                const env = data.environmental_analysis;
                
                resultDiv.innerHTML = `
                    <div class="result-section">
                        <h3>📦 Product Details</h3>
                        <p><strong>Name:</strong> ${product.product_name || 'N/A'}</p>
                        <p><strong>Description:</strong> ${product.product_description || 'N/A'}</p>
                        ${product.materials && product.materials.length > 0 ? 
                            `<p><strong>Materials:</strong> ${product.materials.join(', ')}</p>` : ''}
                        ${product.manufacturing_location ? 
                            `<p><strong>Manufacturing:</strong> ${product.manufacturing_location}</p>` : ''}
                        ${product.packaging_info ? 
                            `<p><strong>Packaging:</strong> ${product.packaging_info}</p>` : ''}
                    </div>
                    
                    <div class="result-section">
                        <h3>🌍 Environmental Sustainability 
                            <span class="score ${getScoreClass(env.sustainability_score)}">
                                ${env.sustainability_score}/10
                            </span>
                        </h3>
                        
                        <h4 style="color: #4CAF50;">✅ Positive Environmental Aspects:</h4>
                        <ul class="result-list">
                            ${env.positive_aspects?.map(item => `<li>• ${item}</li>`).join('') || '<li>No positive aspects identified</li>'}
                        </ul>
                        
                        <h4 style="color: #f44336; margin-top: 15px;">⚠️ Environmental Concerns:</h4>
                        <ul class="result-list">
                            ${env.negative_aspects?.map(item => `<li>• ${item}</li>`).join('') || '<li>No concerns identified</li>'}
                        </ul>
                        
                        <h4 style="color: #ff9800; margin-top: 15px;">� Sustainable Alternatives:</h4>
                        <ul class="result-list">
                            ${env.alternatives?.map(item => `<li>• ${item}</li>`).join('') || '<li>No alternatives suggested</li>'}
                        </ul>
                    </div>
                    
                    <div class="result-section">
                        <h3>🎯 Environmental Recommendation</h3>
                        <p style="font-size: 1.1rem; line-height: 1.6;">${data.recommendation || 'No recommendation available'}</p>
                    </div>
                `;
                
                resultDiv.style.display = 'block';
            }

            function displayDIYResult(data) {
                hideLoading();
                
                const resultDiv = document.getElementById('result');
                const projects = data.projects;
                
                resultDiv.innerHTML = `
                    <h2 style="text-align: center; color: #4CAF50; margin-bottom: 30px;">🔨 Enhanced DIY Project Ideas</h2>
                    
                    ${data.tutorial_sources && data.tutorial_sources.length > 0 ? `
                        <div style="background: #e8f5e8; padding: 15px; margin-bottom: 20px; border-radius: 8px;">
                            <h4>📚 Based on Real Online Tutorials:</h4>
                            <ul style="margin: 10px 0;">
                                ${data.tutorial_sources.map(source => 
                                    `<li><a href="${source.url}" target="_blank" style="color: #2196F3;">${source.title}</a></li>`
                                ).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${Object.entries(projects).map(([difficulty, project]) => `
                        <div class="diy-project">
                            <div class="difficulty ${difficulty.toLowerCase()}">${difficulty.toUpperCase()}</div>
                            <h3>${project.project_name}</h3>
                            <p><strong>⏱️ Estimated Time:</strong> ${project.estimated_time}</p>
                            
                            ${project.generated_image ? `
                                <div style="text-align: center; margin: 20px 0;">
                                    <h4>🎨 AI-Generated Final Product Preview:</h4>
                                    <img src="${project.generated_image.url}" 
                                         alt="Generated ${project.project_name}" 
                                         style="max-width: 100%; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); cursor: pointer;"
                                         onclick="window.open('${project.generated_image.url}', '_blank')">
                                    <p style="font-size: 0.9em; color: #666; margin-top: 10px;">
                                        ✨ Click image to view full size • Generated using real tutorial insights
                                    </p>
                                </div>
                            ` : ''}
                            
                            <h4>🛠️ Materials Required:</h4>
                            <ul class="result-list">
                                ${project.materials_required?.map(material => 
                                    `<li>• ${material.Material || material.material || 'Material'}: ${material.Quantity || material.quantity || 'As needed'}</li>`
                                ).join('') || '<li>Materials list not available</li>'}
                            </ul>
                            
                            <h4>📋 Step-by-Step Instructions:</h4>
                            <ol style="padding-left: 20px;">
                                ${project.steps?.map(step => 
                                    `<li style="margin-bottom: 15px; padding: 10px; background: #f9f9f9; border-left: 4px solid #4CAF50; border-radius: 4px;">
                                        <strong>Step ${step.Step_Number || step.step_number || ''}:</strong> 
                                        ${step.Description || step.description || step.instruction || 'Step description not available'}
                                        ${step.Estimated_Time || step.estimated_time ? `<br><em style="color: #666;">⏱️ Time: ${step.Estimated_Time || step.estimated_time}</em>` : ''}
                                        ${step.Safety_Tips || step.safety_tips ? `<br><em style="color: #f44336;">⚠️ Safety: ${step.Safety_Tips || step.safety_tips}</em>` : ''}
                                    </li>`
                                ).join('') || '<li>Steps not available</li>'}
                            </ol>
                            
                            <h4>⚠️ Safety Tips:</h4>
                            <ul class="result-list">
                                ${project.safety_tips?.map(tip => `<li>• ${tip}</li>`).join('') || '<li>Follow general safety precautions</li>'}
                            </ul>
                            
                            <h4>🎨 Project Description:</h4>
                            <p style="font-style: italic; background: #f0f8f0; padding: 15px; border-radius: 8px;">
                                ${project.image_description || 'A creative upcycled item ready to use!'}
                            </p>
                            
                            ${project.environmental_benefits ? `
                                <h4>🌱 Environmental Benefits:</h4>
                                <p style="color: #2e7d32; background: #e8f5e8; padding: 10px; border-radius: 6px;">
                                    ${project.environmental_benefits}
                                </p>
                            ` : ''}
                        </div>
                    `).join('')}
                    
                    <div style="margin-top: 30px; padding: 20px; background: linear-gradient(135deg, #e8f5e8, #f0f8f0); border-radius: 12px; text-align: center;">
                        <h4 style="color: #2e7d32; margin-bottom: 15px;">🌟 Enhanced with Real Data</h4>
                        <p style="color: #555;">These projects are enhanced using live web search and real tutorial data to provide you with practical, tested upcycling ideas.</p>
                        <div style="margin-top: 15px; font-size: 0.9em; color: #666;">
                            <span>🔍 Web Research</span> • 
                            <span>🧠 AI Analysis</span> • 
                            <span>🎨 AI-Generated Images</span> • 
                            <span>📚 Real Tutorials</span>
                        </div>
                    </div>
                `;
                
                resultDiv.style.display = 'block';
            }

            // Drag and drop functionality
            document.querySelectorAll('.upload-area').forEach(area => {
                ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                    area.addEventListener(eventName, preventDefaults, false);
                });

                ['dragenter', 'dragover'].forEach(eventName => {
                    area.addEventListener(eventName, highlight, false);
                });

                ['dragleave', 'drop'].forEach(eventName => {
                    area.addEventListener(eventName, unhighlight, false);
                });

                area.addEventListener('drop', handleDrop, false);
            });

            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            function highlight(e) {
                e.target.closest('.upload-area').classList.add('dragover');
            }

            function unhighlight(e) {
                e.target.closest('.upload-area').classList.remove('dragover');
            }

            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                const fileInput = e.target.closest('.tab-content').querySelector('input[type="file"]');
                
                if (files.length > 0) {
                    fileInput.files = files;
                    fileInput.dispatchEvent(new Event('change'));
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "EcoMatrix API",
        "version": "1.0.0"
    }

@app.post("/analyze-product")
async def analyze_product(file: UploadFile = File(...)):
    """Analyze product for environmental sustainability impact"""
    file_path = None
    try:
        # Save uploaded file
        file_path = await file_service.save_upload(file)
        
        # Analyze product details
        product_details = await ai_service.analyze_product(file_path)
        
        # Analyze environmental impact
        env_analysis = await ai_service.analyze_environmental_impact(product_details)
        
        # Generate environmental recommendation
        recommendation = await ai_service.generate_environmental_recommendation(
            product_details, env_analysis
        )
        
        return {
            "success": True,
            "product_details": product_details,
            "environmental_analysis": env_analysis,
            "recommendation": recommendation
        }
        
    except Exception as e:
        logger.error(f"Error in product analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    finally:
        if file_path:
            file_service.cleanup_file(file_path)

@app.post("/analyze-diy")
async def analyze_diy(file: UploadFile = File(...)):
    """Generate DIY upcycling project ideas from uploaded item"""
    file_path = None
    try:
        # Save uploaded file
        file_path = await file_service.save_upload(file)
        
        # Generate DIY projects
        projects = await ai_service.generate_diy_projects(file_path)
        
        return {
            "success": True,
            "projects": projects
        }
        
    except Exception as e:
        logger.error(f"Error in DIY analysis: {e}")
        raise HTTPException(status_code=500, detail=f"DIY analysis failed: {str(e)}")
    
    finally:
        if file_path:
            file_service.cleanup_file(file_path)

@app.get("/api/info")
async def api_info():
    """Get API information"""
    return {
        "name": "EcoMatrix API",
        "version": "1.0.0",
        "description": "AI-powered sustainability and DIY analysis platform",
        "endpoints": {
            "product_analysis": "/analyze-product",
            "diy_analysis": "/analyze-diy",
            "health": "/health",
            "ui": "/"
        },
        "features": [
            "Product sustainability analysis",
            "Health impact assessment",
            "DIY project generation",
            "Environmental recommendations",
            "Alternative product suggestions"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting EcoMatrix Backend")
    logger.info(f"🌐 UI available at: http://{Config.SERVER_HOST}:{Config.SERVER_PORT}")
    logger.info(f"📚 API docs at: http://{Config.SERVER_HOST}:{Config.SERVER_PORT}/docs")
    
    uvicorn.run(
        "main:app",
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        reload=Config.DEBUG
    )
