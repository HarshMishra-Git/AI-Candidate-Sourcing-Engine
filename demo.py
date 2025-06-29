#!/usr/bin/env python3
"""
Demo script for the AI Sourcing Agent
Demonstrates the complete end-to-end workflow
"""

import json
import time
from datetime import datetime
from main import SourcingAgent

def run_demo():
    """Run complete demo of the sourcing agent"""
    print("🎬 AI SOURCING AGENT DEMO")
    print("=" * 50)
    print("This demo will show the complete workflow of the AI sourcing agent.")
    print("We'll search for candidates, score them, and generate personalized messages.")
    print()
    
    # Sample job descriptions for demo
    job_descriptions = [
        """About the Company:
Windsurf (formerly Codeium) is a Forbes AI 50 company building the future of developer productivity through AI. With over 200 employees and $243M raised across multiple rounds including a Series C, Windsurf provides cutting-edge in-editor autocomplete, chat assistants, and full IDEs powered by proprietary LLMs. Their user base spans hundreds of thousands of developers worldwide, reflecting strong product-market fit and commercial traction.

Roles and Responsibilities:
Train and fine-tune LLMs focused on developer productivity
Design and prioritize experiments for product impact
Analyze results, conduct ablation studies, and document findings
Convert ML discoveries into scalable product features
Participate in the ML reading group and contribute to knowledge sharing

Job Requirements:
2+ years in software engineering with fast promotions
Strong software engineering and systems thinking skills
Proven experience training and iterating on large production neural networks
Strong GPA from a top CS undergrad program (MIT, Stanford, CMU, UIUC, etc.)
Familiarity with tools like Copilot, ChatGPT, or Windsurf is preferred
Deep curiosity for the code generation space
Excellent documentation and experimentation discipline
Prior experience with applied research (not purely academic publishing)
Must be able to work in Mountain View, CA full-time onsite
Excited to build product-facing features from ML research""",
        "Senior Frontend Developer at TechCorp - React, TypeScript, 5+ years experience, remote work available",
        "Data Scientist at AI Startup - PhD in Machine Learning, experience with PyTorch, TensorFlow, remote position"
    ]
    
    try:
        # Initialize agent
        print("🔧 Initializing AI Sourcing Agent...")
        agent = SourcingAgent()
        print("✅ Agent initialized successfully!\n")
        
        # Demo each job description
        for i, job_desc in enumerate(job_descriptions, 1):
            print(f"📋 DEMO JOB {i}/3")
            print("-" * 30)
            print(f"Job: {job_desc[:80]}...")
            print()
            
            # Run pipeline
            result = agent.run_pipeline(
                job_description=job_desc,
                use_cache=True,
                top_candidates=5
            )
            
            # Display results
            if 'error' not in result:
                display_demo_results(result, job_number=i)
            else:
                print(f"❌ Demo job {i} failed: {result['error']}")
            
            print("\n" + "="*50 + "\n")
            
            # Pause between demos
            if i < len(job_descriptions):
                print("⏳ Waiting 5 seconds before next demo...")
                time.sleep(5)
        
        # Demo summary
        print("🎯 DEMO SUMMARY")
        print("-" * 20)
        print(f"✅ Completed demos for {len(job_descriptions)} job descriptions")
        print("🔍 Demonstrated candidate search and discovery")
        print("📊 Showed AI-powered candidate scoring")
        print("✉️ Generated personalized outreach messages")
        print("💾 Results cached for future use")
        
        # Export demo results
        demo_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        demo_filename = f"demo_results_{demo_timestamp}.json"
        
        demo_summary = {
            "demo_timestamp": datetime.now().isoformat(),
            "jobs_processed": len(job_descriptions),
            "job_descriptions": job_descriptions,
            "demo_completed": True
        }
        
        with open(demo_filename, 'w') as f:
            json.dump(demo_summary, f, indent=2)
        
        print(f"📁 Demo summary saved to: {demo_filename}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False
    
    return True

def display_demo_results(result, job_number):
    """Display demo results in a formatted way"""
    print("📊 RESULTS:")
    
    # Basic stats
    print(f"   🔍 Candidates Found: {result['total_candidates_found']}")
    print(f"   📊 Candidates Scored: {result['total_candidates_scored']}")
    print(f"   ⏱️ Processing Time: {result['processing_time']} seconds")
    print(f"   💾 From Cache: {'Yes' if result.get('from_cache', False) else 'No'}")
    
    # Scoring summary
    if result['scoring_summary']['total_candidates'] > 0:
        summary = result['scoring_summary']
        print(f"   📈 Average Score: {summary['average_score']}/10")
        print(f"   🏆 Highest Score: {summary['highest_score']}/10")
    
    print("\n🏅 TOP CANDIDATES:")
    
    # Show top 3 candidates
    for i, candidate in enumerate(result['top_candidates'][:3], 1):
        print(f"\n   {i}. {candidate.get('name', 'Unknown')}")
        print(f"      Score: {candidate.get('fit_score', 0)}/10")
        print(f"      LinkedIn: {candidate.get('url', 'N/A')[:50]}...")
        
        # Show score breakdown
        breakdown = candidate.get('score_breakdown', {})
        if breakdown:
            print("      Score Breakdown:")
            for category, score in breakdown.items():
                print(f"        • {category.replace('_', ' ').title()}: {score}/10")
        
        # Show message preview
        message = candidate.get('message', '')
        if message:
            message_preview = message[:100] + "..." if len(message) > 100 else message
            print(f"      Message Preview: {message_preview}")
    
    # Message statistics
    msg_stats = result['message_statistics']
    print(f"\n✉️ MESSAGE STATS:")
    print(f"   Generated: {msg_stats['successful_generations']}")
    print(f"   Fallbacks: {msg_stats['fallback_messages']}")
    print(f"   Avg Length: {msg_stats['average_length']} chars")

def interactive_demo():
    """Interactive demo where user can input their own job description"""
    print("\n🎮 INTERACTIVE DEMO")
    print("=" * 30)
    print("Enter your own job description to see the agent in action!")
    print()
    
    try:
        # Get user input
        job_description = input("📝 Enter job description: ").strip()
        
        if not job_description:
            print("❌ No job description provided. Skipping interactive demo.")
            return
        
        print(f"\n🚀 Processing your job: {job_description[:50]}...")
        
        # Initialize and run agent
        agent = SourcingAgent()
        result = agent.run_pipeline(job_description, top_candidates=5)
        
        if 'error' not in result:
            display_demo_results(result, job_number="Interactive")
            
            # Ask if user wants to export results
            export_choice = input("\n💾 Export results to file? (y/n): ").lower().strip()
            if export_choice == 'y':
                filename = agent.export_results(result)
                print(f"✅ Results exported to: {filename}")
        else:
            print(f"❌ Interactive demo failed: {result['error']}")
    
    except KeyboardInterrupt:
        print("\n⏹️ Interactive demo cancelled by user.")
    except Exception as e:
        print(f"❌ Interactive demo failed: {e}")

def quick_api_demo():
    """Demo the API functionality"""
    print("\n🌐 API DEMO")
    print("=" * 20)
    print("Starting FastAPI server demo...")
    
    try:
        import requests
        import threading
        import uvicorn
        from api import app
        from config import get_config
        
        config = get_config()
        
        # Start API server in background thread
        def run_server():
            uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        
        # Test API endpoints
        base_url = "http://127.0.0.1:8001"
        
        print(f"🔗 API Server: {base_url}")
        print("📡 Testing endpoints...")
        
        # Health check
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ Health check: PASSED")
            else:
                print("   ❌ Health check: FAILED")
        except:
            print("   ❌ Health check: CONNECTION FAILED")
        
        # Configuration endpoint
        try:
            response = requests.get(f"{base_url}/config", timeout=5)
            if response.status_code == 200:
                print("   ✅ Configuration: PASSED")
            else:
                print("   ❌ Configuration: FAILED")
        except:
            print("   ❌ Configuration: CONNECTION FAILED")
        
        print("📚 API Documentation available at: http://127.0.0.1:8001/docs")
        print("🔧 To test the full /match endpoint, use the interactive API docs!")
        
    except ImportError:
        print("❌ API demo requires additional dependencies (uvicorn, fastapi)")
    except Exception as e:
        print(f"❌ API demo failed: {e}")

def main():
    """Main demo function"""
    print("🎯 Welcome to the AI Sourcing Agent Demo!")
    print("This demo will showcase all features of the recruitment sourcing agent.")
    print()
    
    # Check if configuration is valid
    try:
        from config import validate_config
        if not validate_config():
            print("❌ Configuration validation failed!")
            print("Please ensure you have set the required environment variables:")
            print("   - GROQ_API_KEY (required)")
            print("   - GOOGLE_SEARCH_API_KEY or SERPAPI_KEY (recommended)")
            return
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return
    
    demo_options = [
        ("1", "Full Demo (3 sample jobs)", run_demo),
        ("2", "Interactive Demo (your job)", interactive_demo),
        ("3", "API Demo", quick_api_demo),
        ("4", "All Demos", lambda: [run_demo(), interactive_demo(), quick_api_demo()])
    ]
    
    print("📋 Demo Options:")
    for option, description, _ in demo_options:
        print(f"   {option}. {description}")
    print("   q. Quit")
    print()
    
    while True:
        choice = input("🎮 Choose demo option (1-4, q): ").strip().lower()
        
        if choice == 'q':
            print("👋 Thanks for trying the AI Sourcing Agent Demo!")
            break
        elif choice in ['1', '2', '3']:
            option_func = next((func for opt, _, func in demo_options if opt == choice), None)
            if option_func:
                print()
                option_func()
                print("\n" + "="*50)
        elif choice == '4':
            for _, description, func in demo_options[:-1]:  # Exclude "All Demos"
                print(f"\n🚀 Running: {description}")
                func()
                print("="*50)
        else:
            print("❌ Invalid choice. Please select 1-4 or q.")

if __name__ == "__main__":
    main()
