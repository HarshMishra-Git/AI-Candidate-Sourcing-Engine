#!/usr/bin/env python3
"""
Test script to verify deployment setup
"""

import requests
import json
import time
from datetime import datetime

def test_local_api():
    """Test the local API deployment"""
    print("🧪 Testing Local API Deployment")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:7860/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API not running. Start with: python app.py")
        return False
    
    # Test main endpoint
    test_job = "Software Engineer, ML Research at Windsurf - Looking for Python developers with machine learning experience"
    
    try:
        response = requests.post(
            "http://localhost:7860/huggingface",
            json={
                "job_description": test_job,
                "top_candidates": 3,
                "use_cache": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Main endpoint working")
            print(f"   Candidates found: {result.get('candidates_found', 0)}")
            print(f"   Top candidates: {len(result.get('top_candidates', []))}")
            
            # Show first candidate if available
            if result.get('top_candidates'):
                candidate = result['top_candidates'][0]
                print(f"   Sample candidate: {candidate.get('name', 'Unknown')} - Score: {candidate.get('fit_score', 0)}")
            
            return True
        else:
            print(f"❌ Main endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (API might be processing)")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_remote_api(api_url):
    """Test remote API deployment"""
    print(f"\n🌐 Testing Remote API: {api_url}")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Remote health endpoint working")
        else:
            print(f"❌ Remote health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Remote health check failed: {e}")
        return False
    
    # Test main endpoint
    test_job = "Software Engineer, ML Research at Windsurf - Looking for Python developers with machine learning experience"
    
    try:
        response = requests.post(
            f"{api_url}/huggingface",
            json={
                "job_description": test_job,
                "top_candidates": 3,
                "use_cache": True
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Remote main endpoint working")
            print(f"   Candidates found: {result.get('candidates_found', 0)}")
            print(f"   Top candidates: {len(result.get('top_candidates', []))}")
            return True
        else:
            print(f"❌ Remote main endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Remote request failed: {e}")
        return False

def generate_test_curl(api_url):
    """Generate test curl commands"""
    print(f"\n📋 Test Commands for: {api_url}")
    print("=" * 50)
    
    print("1. Health Check:")
    print(f"curl -X GET '{api_url}/health'")
    
    print("\n2. Main API Test:")
    print(f"""curl -X POST '{api_url}/huggingface' \\
     -H 'Content-Type: application/json' \\
     -d '{{
       "job_description": "Software Engineer, ML Research at Windsurf - Looking for Python developers with machine learning experience",
       "top_candidates": 5,
       "use_cache": true
     }}'""")
    
    print("\n3. API Documentation:")
    print(f"curl -X GET '{api_url}/docs'")

def main():
    """Main test function"""
    print("🚀 SynapseAI Sourcer - Deployment Test")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test local API
    local_success = test_local_api()
    
    # Ask for remote URL
    print("\n" + "=" * 60)
    remote_url = input("Enter your remote API URL (or press Enter to skip): ").strip()
    
    if remote_url:
        if not remote_url.startswith('http'):
            remote_url = f"https://{remote_url}"
        
        remote_success = test_remote_api(remote_url)
        
        if remote_success:
            generate_test_curl(remote_url)
        else:
            print("\n❌ Remote API test failed. Check your deployment.")
    else:
        print("\n⏭️ Skipping remote API test")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Local API: {'✅ Working' if local_success else '❌ Failed'}")
    if remote_url:
        print(f"Remote API: {'✅ Working' if 'remote_success' in locals() and remote_success else '❌ Failed'}")
    
    if local_success:
        print("\n🎉 Local deployment is ready!")
        print("Next steps:")
        print("1. Deploy to HuggingFace Spaces")
        print("2. Test remote endpoints")
        print("3. Record demo video")
        print("4. Submit to Synapse hackathon")
    else:
        print("\n🔧 Fix local issues before deploying")

if __name__ == "__main__":
    main() 