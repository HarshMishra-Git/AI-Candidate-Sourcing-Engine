import os
from typing import Dict, Any

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

# Model Configuration
DEFAULT_MODEL = "llama3-8b-8192"
ALTERNATIVE_MODEL = "llama3-70b-8192"

# Search Configuration
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

# Application Configuration
MAX_CANDIDATES = 20
BATCH_SIZE = 5
TIMEOUT_SECONDS = 30
MAX_RETRIES = 3

# Scoring Rubric Weights
SCORING_RUBRIC = {
    "education": 0.20,
    "career_trajectory": 0.20, 
    "company_relevance": 0.15,
    "experience_match": 0.25,
    "location_match": 0.10,
    "tenure": 0.10
}

# Cache Configuration
CACHE_FILE = "cache.json"
CACHE_EXPIRY_HOURS = 24

# FastAPI Configuration
API_HOST = "127.0.0.1"
API_PORT = 5000

def get_config() -> Dict[str, Any]:
    """Return application configuration dictionary"""
    return {
        "groq_api_key": os.getenv(GROQ_API_KEY),
        "groq_base_url": GROQ_BASE_URL,
        "default_model": DEFAULT_MODEL,
        "alternative_model": ALTERNATIVE_MODEL,
        "google_search_api_key": GOOGLE_SEARCH_API_KEY,
        "google_search_engine_id": GOOGLE_SEARCH_ENGINE_ID,
        "serpapi_key": SERPAPI_KEY,
        "max_candidates": MAX_CANDIDATES,
        "batch_size": 3,
        "timeout_seconds": 60,
        "max_retries": 4,
        "scoring_rubric": SCORING_RUBRIC,
        "cache_file": CACHE_FILE,
        "cache_expiry_hours": CACHE_EXPIRY_HOURS,
        "api_host": API_HOST,
        "api_port": 5000
    }

def validate_config() -> bool:
    """Validate that required configuration is present"""
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY environment variable is required")
        return False

    if not GOOGLE_SEARCH_API_KEY and not SERPAPI_KEY:
        print("WARNING: No search API key found. Using fallback search method.")

    return True