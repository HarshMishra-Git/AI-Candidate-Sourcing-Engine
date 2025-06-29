#!/usr/bin/env python3
"""
HuggingFace Spaces Deployment Entry Point
AI-Powered Recruitment Sourcing Agent
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import our custom modules
from main import SourcingAgent
from config import get_config

# Global agent instance
sourcing_agent = None

# Pydantic models for request/response
class JobRequest(BaseModel):
    job_description: str = Field(..., description="Job description to search candidates for")
    top_candidates: int = Field(default=10, ge=1, le=50, description="Number of top candidates to return")
    use_cache: bool = Field(default=True, description="Whether to use cached results if available")

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

# Initialize FastAPI app
app = FastAPI(
    title="SynapseAI Sourcer",
    description="AI-powered recruitment sourcing agent for LinkedIn candidate discovery - Synapse Hackathon Submission",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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

@app.on_event("startup")
async def startup_event():
    """Initialize the sourcing agent on startup"""
    global sourcing_agent
    try:
        sourcing_agent = SourcingAgent()
        print("✅ SynapseAI Sourcer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Sourcing Agent: {e}")
        raise

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "SynapseAI Sourcer",
        "version": "1.0.0",
        "description": "AI-powered recruitment sourcing agent for LinkedIn candidate discovery",
        "hackathon": "Synapse Annual First Ever AI Hackathon",
        "docs": "/docs",
        "health": "/health",
        "main_endpoint": "POST /match - Complete candidate sourcing pipeline"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_ready": sourcing_agent is not None,
        "hackathon": "Synapse AI Hackathon Submission"
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

# HuggingFace Spaces specific endpoint
@app.post("/huggingface")
async def huggingface_endpoint(request: JobRequest):
    """
    HuggingFace Spaces optimized endpoint
    Returns results in Synapse hackathon format
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
        
        # Check for errors
        if 'error' in result:
            return {
                "error": result['error'],
                "job_description": request.job_description,
                "timestamp": datetime.now().isoformat()
            }
        
        # Format for Synapse hackathon
        formatted_result = {
            "job_id": f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "candidates_found": result['total_candidates_found'],
            "top_candidates": []
        }
        
        # Format top candidates
        for candidate in result['top_candidates']:
            formatted_candidate = {
                "name": candidate.get('name', 'Unknown'),
                "linkedin_url": candidate.get('url', candidate.get('linkedin_url', 'N/A')),
                "fit_score": candidate.get('fit_score', 0.0),
                "score_breakdown": candidate.get('score_breakdown', {}),
                "outreach_message": candidate.get('message', 'No message generated')
            }
            formatted_result["top_candidates"].append(formatted_candidate)
        
        return formatted_result
        
    except Exception as e:
        return {
            "error": str(e),
            "job_description": request.job_description,
            "timestamp": datetime.now().isoformat()
        }

# Configuration endpoint
@app.get("/config")
async def get_configuration():
    """Get current configuration"""
    config = get_config()
    # Remove sensitive information
    safe_config = {
        "max_candidates": config.get("max_candidates"),
        "batch_size": config.get("batch_size"),
        "timeout_seconds": config.get("timeout_seconds"),
        "scoring_rubric": config.get("scoring_rubric"),
        "cache_expiry_hours": config.get("cache_expiry_hours")
    }
    return safe_config

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "hackathon": "Synapse AI Hackathon"
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
            "hackathon": "Synapse AI Hackathon"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860) 