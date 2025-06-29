# SynapseAI Sourcer

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

## 🚀 **Live Deployment**

### **HuggingFace Spaces (Recommended)**
**Live Demo**: [Your HuggingFace Spaces URL]

**API Endpoints:**
- `POST /match` - Complete candidate sourcing pipeline
- `POST /huggingface` - Synapse hackathon format
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

**Example API Request:**
```bash
curl -X POST "https://your-spaces-url.hf.space/huggingface" \
     -H "Content-Type: application/json" \
     -d '{
       "job_description": "Senior Python Developer - 5+ years Django, React, AWS",
       "top_candidates": 10,
       "use_cache": true
     }'
```

## Features

- 🔍 **Intelligent Candidate Discovery**: Search LinkedIn profiles using Google/SerpAPI
- 📊 **AI-Powered Scoring**: Score candidates using Groq LLM with 6-criteria rubric
- ✉️ **Personalized Messages**: Generate custom outreach messages for each candidate
- ⚡ **Scalable Processing**: Batch processing with async/threading support
- 💾 **Smart Caching**: Avoid duplicate processing with intelligent caching
- 🌐 **REST API**: FastAPI endpoint for web deployment
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
cd SynapseAI-Sourcer
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
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

**Test Synapse Hackathon Job:**
```bash
python test_synapse_job.py
```

### FastAPI REST API

**Start the API server:**
```bash
python app.py
```

**Access the API:**
- Server: http://localhost:7860
- Interactive docs: http://localhost:7860/docs
- Health check: http://localhost:7860/health

## 🚀 **Deployment Options**

### **1. HuggingFace Spaces (Recommended)**

**Steps:**
1. Create account at [huggingface.co](https://huggingface.co)
2. Create new Space → Gradio → Python
3. Upload your project files
4. Set environment variables in Space settings
5. Deploy!

**Files needed:**
- `app.py` (main entry point)
- `requirements.txt`
- All Python modules (`main.py`, `search.py`, etc.)
- `README.md`

### **2. Railway**

**Steps:**
1. Connect GitHub repository to Railway
2. Set environment variables
3. Deploy automatically

### **3. Render**

**Steps:**
1. Connect GitHub repository to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python app.py`
4. Set environment variables
5. Deploy!

## API Endpoints

### Main Endpoints

- `POST /match` - Complete sourcing pipeline (search + score + messages)
- `POST /huggingface` - Synapse hackathon format
- `GET /health` - System health check
- `GET /config` - View configuration

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

## 🏆 **Hackathon Submission**

### **Required Files:**
- ✅ GitHub Repository with code
- ✅ README with setup instructions
- ✅ Demo Video (3 minutes max)
- ✅ Brief Write-up (500 words max)
- ✅ Live API endpoint (HuggingFace Spaces)

### **Demo Video Checklist:**
- [ ] Running agent on Windsurf job description
- [ ] Candidates being discovered and scored
- [ ] Generated outreach messages
- [ ] API endpoint demonstration

### **Write-up Topics:**
- [ ] Approach and architecture
- [ ] Challenges faced and solutions
- [ ] Scaling to 100s of jobs
- [ ] Technical decisions and trade-offs

## 🤝 **About the Project**

This project was built for the **Synapse Annual First Ever AI Hackathon** - a challenge to build an autonomous AI agent that sources LinkedIn profiles at scale, scores candidates using fit score algorithms, and generates personalized outreach.

**Built with:**
- Python 3.8+
- FastAPI
- Groq API (LLaMA3 models)
- Google Custom Search API
- BeautifulSoup for web scraping

**Author:** [Your Name]
**Hackathon:** Synapse Annual First Ever AI Hackathon
**Submission Date:** June 30, 2025

---

**Ready to build the future of recruiting?** 🚀
