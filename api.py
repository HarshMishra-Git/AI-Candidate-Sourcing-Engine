#!/usr/bin/env python3
"""
FastAPI REST API for the AI Sourcing Agent
Provides HTTP endpoints for the recruitment pipeline
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from main import SourcingAgent
from config import get_config

# Global agent instance
sourcing_agent = None

# Pydantic models for request/response
class JobRequest(BaseModel):
    job_description: str = Field(..., description="Job description to search candidates for")
    top_candidates: int = Field(default=10, ge=1, le=50, description="Number of top candidates to return")
    use_cache: bool = Field(default=True, description="Whether to use cached results if available")

class CandidateResponse(BaseModel):
    name: str
    linkedin_url: str
    fit_score: float
    score_breakdown: Dict[str, int]
    message: str
    reasoning: Optional[str] = None

class SourcingResponse(BaseModel):
    job_description: str
    top_candidates: List[Dict[str, Any]]
    total_candidates_found: int
    total_candidates_scored: int
    scoring_summary: Dict[str, Any]
    message_statistics: Dict[str, Any]
    processing_time: float
    timestamp: str
    from_cache: bool = False

class ErrorResponse(BaseModel):
    error: str
    timestamp: str
    details: Optional[str] = None

class BatchJobRequest(BaseModel):
    job_descriptions: list
    top_candidates: int = 10
    use_cache: bool = True

# Startup/shutdown events using lifespan
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global sourcing_agent
    try:
        sourcing_agent = SourcingAgent()
        print("✅ Sourcing Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Sourcing Agent: {e}")
        raise
    yield
    # Shutdown
    print("🔄 Shutting down Sourcing Agent...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="AI Sourcing Agent API",
    description="AI-powered recruitment sourcing agent for LinkedIn candidate discovery",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "AI Sourcing Agent API",
        "version": "1.0.0",
        "description": "AI-powered recruitment sourcing agent for LinkedIn candidate discovery",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "match": "POST /match - Complete candidate sourcing pipeline",
            "search": "POST /search - Search candidates only",
            "score": "POST /score - Score candidates only",
            "messages": "POST /messages - Generate messages only"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_ready": sourcing_agent is not None
    }

# Main sourcing endpoint
@app.post("/match", response_model=SourcingResponse)
async def match_candidates(request: JobRequest) -> SourcingResponse:
    """
    Main endpoint to find and score candidates for a job description
    
    This endpoint:
    1. Searches for LinkedIn candidates based on job description
    2. Scores candidates using AI rubric
    3. Generates personalized outreach messages
    4. Returns top candidates with scores and messages
    """
    if not sourcing_agent:
        raise HTTPException(status_code=503, detail="Sourcing agent not initialized")
    
    try:
        # Run the sourcing pipeline
        result = await sourcing_agent.run_pipeline_async(
            job_description=request.job_description,
            use_cache=request.use_cache,
            top_candidates=request.top_candidates
        )
        
        # Check for errors in result
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return SourcingResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Quick search endpoint (candidates only, no scoring)
@app.post("/search")
async def search_candidates_only(request: JobRequest):
    """
    Search for candidates without scoring or message generation
    Faster endpoint for initial candidate discovery
    """
    if not sourcing_agent:
        raise HTTPException(status_code=503, detail="Sourcing agent not initialized")
    
    try:
        # Extract job requirements
        job_requirements = sourcing_agent.groq_client.extract_job_requirements(request.job_description)
        
        # Search for candidates
        candidates = sourcing_agent.searcher.search_candidates(
            request.job_description, 
            job_requirements or {}
        )
        
        return {
            "job_description": request.job_description,
            "job_requirements": job_requirements,
            "candidates": candidates[:request.top_candidates],
            "total_found": len(candidates),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Score candidates endpoint
@app.post("/score")
async def score_candidates_only(job_description: str, candidates: List[Dict[str, Any]]):
    """
    Score a provided list of candidates
    Useful when you have candidates and want to score them
    """
    if not sourcing_agent:
        raise HTTPException(status_code=503, detail="Sourcing agent not initialized")
    
    try:
        scored_candidates = sourcing_agent.scorer.score_candidates_batch(
            job_description, 
            candidates
        )
        
        return {
            "job_description": job_description,
            "scored_candidates": scored_candidates,
            "scoring_summary": sourcing_agent.scorer.get_scoring_summary(scored_candidates),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Generate messages endpoint
@app.post("/messages")
async def generate_messages_only(job_description: str, candidates: List[Dict[str, Any]]):
    """
    Generate outreach messages for a provided list of candidates
    """
    if not sourcing_agent:
        raise HTTPException(status_code=503, detail="Sourcing agent not initialized")
    
    try:
        candidates_with_messages = sourcing_agent.message_generator.generate_messages_batch(
            job_description, 
            candidates
        )
        
        return {
            "job_description": job_description,
            "candidates_with_messages": candidates_with_messages,
            "message_statistics": sourcing_agent.message_generator.get_message_statistics(candidates_with_messages),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cache management endpoints
@app.get("/cache/status")
async def cache_status():
    """Get cache status and statistics"""
    if not sourcing_agent:
        raise HTTPException(status_code=503, detail="Sourcing agent not initialized")
    
    cache_size = len(sourcing_agent.cache)
    cache_keys = list(sourcing_agent.cache.keys())
    
    return {
        "cache_size": cache_size,
        "cache_file": sourcing_agent.cache_file,
        "recent_jobs": cache_keys[:5] if cache_keys else [],
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/cache")
async def clear_cache():
    """Clear the agent cache"""
    if not sourcing_agent:
        raise HTTPException(status_code=503, detail="Sourcing agent not initialized")
    
    sourcing_agent.clear_cache()
    
    return {
        "message": "Cache cleared successfully",
        "timestamp": datetime.now().isoformat()
    }

# Configuration endpoint
@app.get("/config")
async def get_configuration():
    """Get current agent configuration (without sensitive data)"""
    config = get_config()
    
    # Remove sensitive information
    safe_config = {
        "max_candidates": config["max_candidates"],
        "batch_size": config["batch_size"],
        "timeout_seconds": config["timeout_seconds"],
        "max_retries": config["max_retries"],
        "scoring_rubric": config["scoring_rubric"],
        "cache_expiry_hours": config["cache_expiry_hours"],
        "api_host": config["api_host"],
        "api_port": config["api_port"],
        "groq_model": config["default_model"],
        "has_groq_key": bool(config["groq_api_key"]),
        "has_google_search": bool(config["google_search_api_key"]),
        "has_serpapi": bool(config["serpapi_key"])
    }
    
    return safe_config

# Background task for async processing
@app.post("/match/async")
async def match_candidates_async(request: JobRequest, background_tasks: BackgroundTasks):
    """
    Async version of candidate matching
    Returns immediately with a task ID for status checking
    """
    if not sourcing_agent:
        raise HTTPException(status_code=503, detail="Sourcing agent not initialized")
    
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # In a production environment, you'd use a proper task queue like Celery
    # For now, we'll return the task_id and suggest checking back
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Job submitted for processing. Check back in a few minutes.",
        "estimated_completion": "2-5 minutes",
        "timestamp": datetime.now().isoformat()
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "details": str(exc),
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    config = get_config()
    
    print("🚀 Starting AI Sourcing Agent API Server...")
    print(f"📡 Server will be available at: http://{config['api_host']}:{config['api_port']}")
    print(f"📚 API Documentation: http://{config['api_host']}:{config['api_port']}/docs")
    
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=5000,
        reload=True,
        log_level="info",
        access_log=True,
        timeout_keep_alive=120,
        workers=1
    )

@app.post("/huggingface")
async def huggingface_endpoint(request: JobRequest):
    """
    HuggingFace Spaces endpoint: takes job description, returns top 10 candidates with outreach messages in Synapse format
    """
    if not sourcing_agent:
        raise HTTPException(status_code=503, detail="Sourcing agent not initialized")
    try:
        result = await sourcing_agent.run_pipeline_async(
            job_description=request.job_description,
            use_cache=request.use_cache,
            top_candidates=10
        )
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        # Format output as required by Synapse
        output = {
            "job_id": request.job_description[:40].replace(' ', '-').lower(),
            "candidates_found": result['total_candidates_found'],
            "top_candidates": []
        }
        for c in result['top_candidates']:
            output['top_candidates'].append({
                "name": c.get('name', ''),
                "linkedin_url": c.get('linkedin_url', c.get('url', '')),
                "fit_score": c.get('fit_score', 0),
                "score_breakdown": c.get('score_breakdown', {}),
                "outreach_message": c.get('message', '')
            })
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch")
async def batch_jobs(request: BatchJobRequest):
    """
    Batch endpoint: process multiple jobs in parallel and return results in Synapse format
    """
    if not sourcing_agent:
        raise HTTPException(status_code=503, detail="Sourcing agent not initialized")
    try:
        results = sourcing_agent.run_batch_jobs(
            job_descriptions=request.job_descriptions,
            use_cache=request.use_cache,
            top_candidates=request.top_candidates
        )
        # Format output for each job
        output = []
        for result in results:
            if 'error' in result:
                output.append({'error': result['error'], 'job_description': result.get('job_description', '')})
                continue
            job_out = {
                "job_id": result['job_description'][:40].replace(' ', '-').lower(),
                "candidates_found": result['total_candidates_found'],
                "top_candidates": []
            }
            for c in result['top_candidates']:
                job_out['top_candidates'].append({
                    "name": c.get('name', ''),
                    "linkedin_url": c.get('linkedin_url', c.get('url', '')),
                    "fit_score": c.get('fit_score', 0),
                    "score_breakdown": c.get('score_breakdown', {}),
                    "outreach_message": c.get('message', '')
                })
            output.append(job_out)
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
