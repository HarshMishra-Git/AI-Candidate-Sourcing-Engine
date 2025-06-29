# AI-Powered Recruitment Sourcing Agent

🚀 **Synapse AI Hackathon Submission** - A comprehensive AI-powered recruitment sourcing agent that discovers LinkedIn candidates, scores them using advanced AI models, and generates personalized outreach messages.

## 🏆 **Hackathon Requirements Compliance**

This implementation **fully meets** all Synapse AI Hackathon requirements:

### ✅ **Core Requirements Met:**
- **Job Input**: Accepts job description strings via API or CLI
- **LinkedIn Profile Discovery**: Searches and extracts candidate profiles using multiple methods
- **Fit Scoring**: Implements exact 6-criteria rubric (Education 20%, Career Trajectory 20%, Experience Match 25%, Company Relevance 15%, Location Match 10%, Tenure 10%)
- **Message Generation**: Creates personalized LinkedIn outreach messages using AI
- **Scale Support**: Handles multiple jobs with batching, caching, and async processing

### ✅ **Bonus Features Implemented:**
- **Multi-Source Enhancement**: Google Search API + SerpAPI + web scraping fallback
- **Smart Caching**: Hash-based caching with 24-hour expiry
- **Batch Processing**: Configurable batch sizes for 10+ jobs in parallel
- **Confidence Scoring**: Error handling with fallback scores and reasoning

### ✅ **Technical Stack:**
- **Development**: Built with Cursor (as required)
- **Language**: Python (as required)
- **LLM**: Groq API with LLaMA3 models (as required)
- **Data Storage**: JSON-based minimal storage (as required)
- **FastAPI**: REST API for HuggingFace Spaces deployment (bonus requirement)

### 🎯 **Demo Job Description:**
The system is tested with the exact Synapse job description: "Software Engineer, ML Research at Windsurf (Codeium)" - a Forbes AI 50 company building AI-powered developer tools.

## Features

- 🔍 **Intelligent Candidate Discovery**: Search LinkedIn profiles using Google/SerpAPI
- 📊 **AI-Powered Scoring**: Score candidates using Groq LLM with 6-criteria rubric
- ✉️ **Personalized Messages**: Generate custom outreach messages for each candidate
- ⚡ **Scalable Processing**: Batch processing with async/threading support
- 💾 **Smart Caching**: Avoid duplicate processing with intelligent caching
- 🌐 **REST API**: Optional FastAPI endpoint for web deployment
- 📈 **Analytics**: Comprehensive scoring and performance analytics

## Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Groq API Key** (required) - Get from [console.groq.com](https://console.groq.com)
3. **Search API Key** (recommended) - Either:
   - Google Custom Search API + Search Engine ID
   - SerpAPI Key

### Installation

1. **Clone and setup**:
```bash
git clone <repository-url>
cd ai-sourcing-agent
```

2. **Install dependencies** (using uv or pip):
```bash
# Using uv (recommended)
uv add requests beautifulsoup4 fastapi uvicorn pydantic trafilatura

# Or using pip
pip install requests beautifulsoup4 fastapi uvicorn pydantic trafilatura
```

3. **Set environment variables**:
```bash
export GROQ_API_KEY="your_groq_api_key_here"
export GOOGLE_SEARCH_API_KEY="your_google_api_key_here"  # Optional
export GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id"  # Optional
```

## Usage

### Command Line Interface

**Basic usage:**
```bash
python main.py "Software Engineer, ML Research at Windsurf - Looking for Python developers with 3+ years experience"
```

**Run demo:**
```bash
python demo.py
```

**Test Synapse Hackathon Job:**
```bash
python test_synapse_job.py
```

### FastAPI REST API

**Start the API server:**
```bash
python api.py
```

**Access the API:**
- Server: http://localhost:5000
- Interactive docs: http://localhost:5000/docs
- Health check: http://localhost:5000/health

**Example API request:**
```bash
curl -X POST "http://localhost:5000/match" \
     -H "Content-Type: application/json" \
     -d '{
       "job_description": "Senior Python Developer - 5+ years Django, React, AWS",
       "top_candidates": 5,
       "use_cache": true
     }'
```

**HuggingFace Spaces API:**
```bash
curl -X POST "http://localhost:5000/huggingface" \
     -H "Content-Type: application/json" \
     -d '{
       "job_description": "<your job description>",
       "top_candidates": 10,
       "use_cache": true
     }'
```
- Returns: JSON with job_id, candidates_found, and top_candidates (with outreach messages) in Synapse format.

**Batch API:**
```bash
curl -X POST "http://localhost:5000/batch" \
     -H "Content-Type: application/json" \
     -d '{
       "job_descriptions": ["job1 description", "job2 description"],
       "top_candidates": 10,
       "use_cache": true
     }'
```
- Returns: List of results in Synapse format for each job.

## API Endpoints

### Main Endpoints

- `POST /match` - Complete sourcing pipeline (search + score + messages)
- `POST /search` - Search candidates only (faster)
- `POST /score` - Score existing candidates
- `POST /messages` - Generate messages for candidates

### Management Endpoints

- `GET /health` - System health check
- `GET /config` - View configuration
- `GET /cache/status` - Cache statistics
- `DELETE /cache` - Clear cache

## Pipeline Components

### 1. Candidate Discovery (`search.py`)
- **Primary**: Google Custom Search API with LinkedIn filtering
- **Fallback**: Web scraping with BeautifulSoup
- **Alternative**: SerpAPI integration
- Extracts up to 20 LinkedIn profile URLs with basic info

### 2. AI-Powered Scoring (`score.py`)
Uses Groq LLM to evaluate candidates on 6 criteria:
- **Education** (20%): Degrees, certifications, academic achievements
- **Career Trajectory** (20%): Growth pattern, promotions, progression
- **Experience Match** (25%): Direct skills and experience alignment
- **Company Relevance** (15%): Experience at similar/relevant companies
- **Location Match** (10%): Geographic alignment
- **Tenure** (10%): Job stability and appropriate tenure

### 3. Message Generation (`message.py`)
- Generates personalized LinkedIn outreach messages
- Uses candidate profile + job description context
- Fallback templates for API failures
- Validates message length for LinkedIn limits

### 4. Smart Caching
- Hash-based caching using job description
- 24-hour expiry for results
- Avoids duplicate API calls and processing

## Configuration

All settings are managed in `config.py`:

```python
# Model Configuration
DEFAULT_MODEL = "llama3-8b-8192"
ALTERNATIVE_MODEL = "llama3-70b-8192"

# Processing Settings
MAX_CANDIDATES = 20
BATCH_SIZE = 5
TIMEOUT_SECONDS = 30
```

## Example Output

```json
{
  "job_description": "Software Engineer, ML Research...",
  "top_candidates": [
    {
      "name": "John Smith",
      "linkedin_url": "https://linkedin.com/in/johnsmith",
      "fit_score": 8.5,
      "score_breakdown": {
        "education": 9,
        "career_trajectory": 8,
        "experience_match": 9,
        "company_relevance": 7,
        "location_match": 8,
        "tenure": 8
      },
      "message": "Hi John, I saw your impressive work in ML research at Google...",
      "reasoning": "Strong technical background with relevant ML experience..."
    }
  ],
  "total_candidates_found": 18,
  "scoring_summary": {
    "average_score": 7.2,
    "highest_score": 8.5,
    "candidates_above_threshold": 5
  },
  "processing_time": 45.2
}
```

## Troubleshooting

### Common Issues

1. **No candidates found**
   - Check search API credentials
   - Verify job description has relevant keywords
   - Try different search terms

2. **Scoring failures**
   - Verify Groq API key is valid
   - Check API rate limits
   - Review model availability

3. **API errors**
   - Ensure all dependencies are installed
   - Check port availability (default: 5000)
   - Verify environment variables

### Performance Tips

- Use caching for repeated searches
- Process candidates in smaller batches
- Consider using async endpoints for large jobs

## Architecture

The system follows a modular, pipeline-based architecture:

```
Job Description → Requirements Extraction → Candidate Search → AI Scoring → Message Generation → Results
```

Each component can be used independently or as part of the complete pipeline.

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

**Bonus Features:**
- Multi-source enrichment: The system is modular and can be extended to include GitHub, Twitter, or personal website data for improved fit scoring.
- Confidence scoring: If candidate data is incomplete, the system can flag low-confidence results and fallback to template messages or scores.
