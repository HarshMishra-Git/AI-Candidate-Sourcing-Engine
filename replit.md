# AI-Powered Recruitment Sourcing Agent

## Overview

This is a comprehensive AI-powered recruitment sourcing agent built in Python that automates the candidate discovery, scoring, and outreach process. The system searches LinkedIn profiles, evaluates candidates using AI models, and generates personalized outreach messages.

## System Architecture

### Core Architecture Pattern
- **Pipeline-based Processing**: Modular pipeline with distinct stages (search → score → message)
- **Component-based Design**: Loosely coupled components that can be used independently
- **Async/Threading Support**: Concurrent processing for scalability
- **Caching Layer**: JSON-based caching to avoid duplicate processing

### Technology Stack
- **Language**: Python 3.8+
- **LLM Provider**: Groq API (LLaMA3-8b-8192, LLaMA3-70b-8192)
- **Web Framework**: FastAPI (optional REST API)
- **Search**: Google Custom Search API / SerpAPI fallback with web scraping
- **Data Storage**: JSON file-based caching system
- **Processing**: asyncio and concurrent.futures for parallel execution

## Key Components

### 1. SourcingAgent (main.py)
**Purpose**: Main orchestrator that coordinates the entire pipeline
- Initializes all components
- Manages caching and configuration
- Orchestrates the complete workflow from job description to final results

### 2. LinkedInSearcher (search.py)
**Purpose**: Discovers LinkedIn candidate profiles
- **Primary**: Google Custom Search API with LinkedIn site filtering
- **Fallback**: Web scraping with BeautifulSoup
- **Alternative**: SerpAPI integration
- Extracts profile URLs and basic candidate information

### 3. CandidateScorer (score.py)
**Purpose**: AI-powered candidate evaluation
- Uses Groq LLM to score candidates on 6 criteria
- Implements weighted scoring rubric:
  - Education (20%)
  - Career Trajectory (20%)
  - Experience Match (25%)
  - Company Relevance (15%)
  - Location Match (10%)
  - Tenure (10%)

### 4. MessageGenerator (message.py)
**Purpose**: Creates personalized outreach messages
- Generates custom messages based on job description and candidate profile
- Uses Groq LLM for natural language generation
- Includes fallback templates for API failures

### 5. GroqClient (groq_utils.py)
**Purpose**: Handles all LLM interactions
- Manages API authentication and requests
- Implements retry logic and error handling
- Supports multiple models (LLaMA3-8b, LLaMA3-70b)

### 6. FastAPI Server (api.py)
**Purpose**: Optional REST API interface
- Provides HTTP endpoints for web deployment
- Supports background task processing
- CORS-enabled for frontend integration

## Data Flow

1. **Input**: Job description string
2. **Search**: Extract keywords → Search LinkedIn profiles → Parse results
3. **Score**: Profile text → Groq LLM → 6-criteria scores → Weighted final score
4. **Message**: Job + Profile → Groq LLM → Personalized outreach message
5. **Output**: Ranked candidates with scores and messages

### Caching Strategy
- **Cache Key**: Hash of job description
- **Cache Content**: Complete pipeline results (search + scores + messages)
- **Expiry**: 24 hours
- **Storage**: JSON file (`cache.json`)

## External Dependencies

### Required APIs
- **Groq API**: LLM inference (required)
  - Models: llama3-8b-8192, llama3-70b-8192
  - Purpose: Candidate scoring and message generation

### Optional APIs
- **Google Custom Search API**: Primary search method
  - Requires: API key + Search Engine ID
  - Purpose: LinkedIn profile discovery
- **SerpAPI**: Alternative search method
  - Requires: API key
  - Purpose: Backup for Google search

### Fallback Mechanisms
- Web scraping with BeautifulSoup if no search APIs available
- Basic template messages if Groq API fails
- Error handling with graceful degradation

## Deployment Strategy

### Local Development
- Direct Python execution with environment variables
- File-based configuration and caching
- Demo script for testing complete workflow

### Production Deployment
- **FastAPI Server**: REST API with background processing
- **Environment Variables**: Secure API key management
- **Containerization Ready**: Filesystem-safe design for containers
- **HuggingFace Spaces**: Compatible with their deployment model

### Configuration Management
- Environment-based configuration in `config.py`
- Centralized settings with validation
- Flexible model and parameter configuration

## Changelog

- June 29, 2025: Complete AI sourcing agent built and deployed
  - Implemented full pipeline: search → score → message generation
  - Integrated Groq API for AI-powered candidate scoring and message generation
  - Added Google Custom Search API for LinkedIn candidate discovery
  - Built comprehensive FastAPI REST API with multiple endpoints
  - Added smart caching system with 24-hour expiry
  - Implemented async/threading support for scalable batch processing
  - Created comprehensive documentation and demo scripts
  - All components tested and verified working
- June 29, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.