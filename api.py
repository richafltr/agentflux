#!/usr/bin/env python3
"""
Web interface for Agentic Designer
Provides REST API and simple web UI for design system extraction
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import aiofiles
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
import uvicorn

from vision_analyzer import VisionAnalyzer
from config import Config

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Designer API",
    description="AI-powered design system extraction from website screenshots",
    version="1.0.0"
)

# Create directories
Path("results").mkdir(exist_ok=True)
Path("screenshots").mkdir(exist_ok=True)

# Global analyzer instance
analyzer = VisionAnalyzer()

# Pydantic models
class AnalysisRequest(BaseModel):
    url: HttpUrl
    include_mobile: bool = False
    save_screenshot: bool = True
    multi_stage: bool = True

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    url: str
    created_at: str
    completed_at: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# In-memory storage for analysis results (use database in production)
analysis_storage: Dict[str, AnalysisResponse] = {}

@app.get("/", response_class=HTMLResponse)
async def root():
    """Simple web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agentic Designer</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px; 
                margin: 0 auto; 
                padding: 2rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 2rem;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            h1 { 
                text-align: center; 
                margin-bottom: 2rem;
                font-size: 2.5rem;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .subtitle {
                text-align: center;
                margin-bottom: 2rem;
                opacity: 0.9;
                font-size: 1.1rem;
            }
            form { 
                display: flex; 
                flex-direction: column; 
                gap: 1rem; 
                margin-bottom: 2rem;
            }
            input[type="url"] { 
                padding: 1rem; 
                border: none;
                border-radius: 10px;
                font-size: 1rem;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
            }
            .options {
                display: flex;
                gap: 1rem;
                flex-wrap: wrap;
            }
            .checkbox-group {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                background: rgba(255, 255, 255, 0.1);
                padding: 0.5rem 1rem;
                border-radius: 10px;
            }
            button { 
                padding: 1rem 2rem; 
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                color: white; 
                border: none; 
                border-radius: 10px;
                font-size: 1rem;
                cursor: pointer;
                transition: transform 0.2s;
            }
            button:hover { 
                transform: translateY(-2px);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            #status { 
                margin-top: 1rem; 
                padding: 1rem;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.1);
                display: none;
            }
            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255,255,255,0.3);
                border-radius: 50%;
                border-top-color: #fff;
                animation: spin 1s ease-in-out infinite;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            .result-link {
                color: #4ecdc4;
                text-decoration: none;
                font-weight: bold;
            }
            .result-link:hover {
                text-decoration: underline;
            }
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1rem;
                margin: 2rem 0;
            }
            .feature-card {
                background: rgba(255, 255, 255, 0.1);
                padding: 1.5rem;
                border-radius: 15px;
                text-align: center;
            }
            .feature-icon {
                font-size: 2rem;
                margin-bottom: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 Agentic Designer</h1>
            <p class="subtitle">AI-powered design system extraction from website screenshots</p>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">🔍</div>
                    <h3>Deep Analysis</h3>
                    <p>Extract typography, colors, spacing, and layout patterns with AI precision</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📱</div>
                    <h3>Multi-Device</h3>
                    <p>Analyze both desktop and mobile views for comprehensive insights</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <h3>Multi-Stage</h3>
                    <p>Advanced multi-stage analysis for enhanced accuracy and detail</p>
                </div>
            </div>
            
            <form id="analysisForm">
                <input type="url" id="url" placeholder="Enter website URL (e.g., https://agentops.ai)" required>
                
                <div class="options">
                    <div class="checkbox-group">
                        <input type="checkbox" id="includeMobile" name="includeMobile">
                        <label for="includeMobile">📱 Include Mobile Analysis</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="multiStage" name="multiStage" checked>
                        <label for="multiStage">⚡ Multi-Stage Analysis</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="saveScreenshot" name="saveScreenshot" checked>
                        <label for="saveScreenshot">📸 Save Screenshot</label>
                    </div>
                </div>
                
                <button type="submit" id="submitBtn">
                    Analyze Design System
                </button>
            </form>
            
            <div id="status"></div>
        </div>

        <script>
            const form = document.getElementById('analysisForm');
            const status = document.getElementById('status');
            const submitBtn = document.getElementById('submitBtn');
            
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const url = document.getElementById('url').value;
                const includeMobile = document.getElementById('includeMobile').checked;
                const multiStage = document.getElementById('multiStage').checked;
                const saveScreenshot = document.getElementById('saveScreenshot').checked;
                
                // Show loading
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="loading"></span> Analyzing...';
                status.style.display = 'block';
                status.innerHTML = '🚀 Starting analysis...';
                
                try {
                    // Start analysis
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            url: url,
                            include_mobile: includeMobile,
                            multi_stage: multiStage,
                            save_screenshot: saveScreenshot
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(result.detail || 'Analysis failed');
                    }
                    
                    // Poll for results
                    const analysisId = result.analysis_id;
                    pollResults(analysisId);
                    
                } catch (error) {
                    status.innerHTML = `❌ Error: ${error.message}`;
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'Analyze Design System';
                }
            });
            
            async function pollResults(analysisId) {
                try {
                    const response = await fetch(`/api/analysis/${analysisId}`);
                    const result = await response.json();
                    
                    if (result.status === 'completed') {
                        status.innerHTML = `
                            ✅ Analysis complete! 
                            <a href="/api/analysis/${analysisId}/download" class="result-link" target="_blank">
                                Download Results
                            </a>
                        `;
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = 'Analyze Design System';
                    } else if (result.status === 'failed') {
                        status.innerHTML = `❌ Analysis failed: ${result.error}`;
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = 'Analyze Design System';
                    } else {
                        // Still processing
                        status.innerHTML = '🔄 Processing... This may take a few minutes.';
                        setTimeout(() => pollResults(analysisId), 3000);
                    }
                } catch (error) {
                    status.innerHTML = `❌ Error checking status: ${error.message}`;
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'Analyze Design System';
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/analyze")
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start a new design analysis"""
    
    # Generate analysis ID
    analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Create analysis record
    analysis_record = AnalysisResponse(
        analysis_id=analysis_id,
        status="processing",
        url=str(request.url),
        created_at=datetime.now().isoformat()
    )
    
    analysis_storage[analysis_id] = analysis_record
    
    # Start background analysis
    background_tasks.add_task(
        run_analysis,
        analysis_id,
        str(request.url),
        request.include_mobile,
        request.save_screenshot,
        request.multi_stage
    )
    
    return {"analysis_id": analysis_id, "status": "processing"}

@app.get("/api/analysis/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get analysis status and results"""
    
    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_storage[analysis_id]

@app.get("/api/analysis/{analysis_id}/download")
async def download_analysis_results(analysis_id: str):
    """Download analysis results as JSON file"""
    
    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_storage[analysis_id]
    
    if analysis.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    # Create temporary file
    results_file = Path("results") / f"{analysis_id}.json"
    
    if not results_file.exists():
        # Create file from stored results
        async with aiofiles.open(results_file, 'w') as f:
            await f.write(json.dumps(analysis.results, indent=2))
    
    return FileResponse(
        path=results_file,
        filename=f"design_analysis_{analysis_id}.json",
        media_type="application/json"
    )

async def run_analysis(
    analysis_id: str,
    url: str,
    include_mobile: bool,
    save_screenshot: bool,
    multi_stage: bool
):
    """Background task to run the analysis"""
    
    try:
        # Run the analysis
        results = await analyzer.analyze_website(
            url=url,
            save_screenshot=save_screenshot,
            include_mobile=include_mobile
        )
        
        # Add metadata
        results["metadata"] = {
            "analysis_id": analysis_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "multi_stage_analysis": multi_stage,
            "include_mobile": include_mobile,
            "tool_version": "1.0.0"
        }
        
        # Update storage
        analysis_storage[analysis_id].status = "completed"
        analysis_storage[analysis_id].completed_at = datetime.now().isoformat()
        analysis_storage[analysis_id].results = results
        
        # Save to file
        results_file = Path("results") / f"{analysis_id}.json"
        async with aiofiles.open(results_file, 'w') as f:
            await f.write(json.dumps(results, indent=2))
        
    except Exception as e:
        # Update storage with error
        analysis_storage[analysis_id].status = "failed"
        analysis_storage[analysis_id].error = str(e)
        analysis_storage[analysis_id].completed_at = datetime.now().isoformat()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        Config.validate()
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agentic Designer Web App")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print("🎨 Starting Agentic Designer Web App...")
    print(f"📡 Server will be available at: http://{args.host}:{args.port}")
    print("💡 Make sure your OPENAI_API_KEY is set in environment variables or .env file")
    
    uvicorn.run(
        "api:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    ) 