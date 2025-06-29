# 🚀 Deployment Guide - SynapseAI Sourcer

This guide will help you deploy your AI Sourcing Agent to various platforms for the Synapse hackathon.

## 🎯 **Recommended: HuggingFace Spaces**

### **Why HuggingFace Spaces?**
- ✅ **Free hosting**
- ✅ **Perfect for hackathon demos**
- ✅ **FastAPI support**
- ✅ **Easy environment variable setup**
- ✅ **Professional appearance**

### **Step-by-Step Deployment**

#### **1. Prepare Your Repository**
```bash
# Clean up unnecessary files
rm -rf __pycache__/
rm -f cache.json
rm -f sourcing_results_*.json
rm -f demo.py
rm -f replit.md
rm -f .replit
rm -rf frontend/
```

#### **2. Create HuggingFace Account**
1. Go to [huggingface.co](https://huggingface.co)
2. Sign up for a free account
3. Verify your email

#### **3. Create New Space**
1. Click "New Space" on your profile
2. Choose settings:
   - **Owner**: Your username
   - **Space name**: `synapse-ai-sourcer`
   - **License**: MIT
   - **SDK**: **Gradio** (not Gradio!)
   - **Python version**: 3.9

#### **4. Upload Your Files**
Upload these files to your Space:
- `app.py` (main entry point)
- `requirements.txt`
- `main.py`
- `search.py`
- `score.py`
- `message.py`
- `groq_utils.py`
- `config.py`
- `test_synapse_job.py`
- `README.md`

#### **5. Set Environment Variables**
In your Space settings, add these environment variables:
```
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_SEARCH_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

#### **6. Deploy**
1. Commit your changes
2. Wait for build to complete (2-3 minutes)
3. Your API will be live at: `https://your-username-synapse-ai-sourcer.hf.space`

### **Test Your Deployment**
```bash
curl -X POST "https://your-username-synapse-ai-sourcer.hf.space/huggingface" \
     -H "Content-Type: application/json" \
     -d '{
       "job_description": "Software Engineer, ML Research at Windsurf - Looking for Python developers with machine learning experience",
       "top_candidates": 5,
       "use_cache": true
     }'
```

## 🌐 **Alternative: Railway**

### **Step-by-Step**

#### **1. Connect GitHub**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"

#### **2. Configure Project**
1. Select your repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python app.py`
4. Set port: `7860`

#### **3. Environment Variables**
Add these in Railway dashboard:
```
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_SEARCH_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

#### **4. Deploy**
1. Railway will automatically deploy
2. Get your live URL from the dashboard

## ☁️ **Alternative: Render**

### **Step-by-Step**

#### **1. Connect Repository**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"

#### **2. Configure Service**
1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python app.py`
4. Choose plan: Free

#### **3. Environment Variables**
Add these in Render dashboard:
```
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_SEARCH_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

#### **4. Deploy**
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Get your live URL

## 🔧 **Local Testing**

### **Test Before Deployment**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your_groq_api_key_here"

# Test the API locally
python app.py

# In another terminal, test the API
curl -X POST "http://localhost:7860/huggingface" \
     -H "Content-Type: application/json" \
     -d '{
       "job_description": "Software Engineer, ML Research at Windsurf",
       "top_candidates": 3,
       "use_cache": false
     }'
```

## 📋 **Deployment Checklist**

### **Before Deployment**
- [ ] All files are committed to GitHub
- [ ] `requirements.txt` is up to date
- [ ] `app.py` is the main entry point
- [ ] Environment variables are ready
- [ ] Local testing works

### **After Deployment**
- [ ] Health check endpoint works (`/health`)
- [ ] API documentation is accessible (`/docs`)
- [ ] Main endpoint responds (`/huggingface`)
- [ ] Test with Synapse job description
- [ ] Update README with live URL

## 🎥 **Demo Video Setup**

### **For Demo Video**
1. **Show local development** (30 seconds)
2. **Deploy to HuggingFace Spaces** (30 seconds)
3. **Test with Windsurf job** (1 minute)
4. **Show API endpoints** (30 seconds)
5. **Display results and scoring** (30 seconds)

### **Demo Script**
```
"Hi, I'm [Your Name] and this is my SynapseAI Sourcer for the Synapse hackathon.

Let me show you how it works:
1. I'll input the Windsurf job description
2. The system searches LinkedIn for candidates
3. Scores them using AI on 6 criteria
4. Generates personalized outreach messages
5. Here's the live API endpoint..."

[Show live demo with real job description]
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Build Fails**
- Check `requirements.txt` has all dependencies
- Verify Python version compatibility
- Check for syntax errors in code

#### **API Not Responding**
- Verify environment variables are set
- Check logs for error messages
- Ensure port 7860 is correct

#### **No Candidates Found**
- Check search API credentials
- Verify job description has relevant keywords
- Test with simpler job description first

#### **Scoring Fails**
- Verify Groq API key is valid
- Check API rate limits
- Review model availability

## 📞 **Support**

If you encounter issues:
1. Check the logs in your deployment platform
2. Test locally first
3. Verify all environment variables
4. Check API documentation

## 🏆 **Hackathon Submission**

### **Final Steps**
1. ✅ Deploy to HuggingFace Spaces
2. ✅ Test all endpoints
3. ✅ Record demo video
4. ✅ Update README with live URL
5. ✅ Submit to Synapse hackathon form

**Good luck with your submission!** 🚀 