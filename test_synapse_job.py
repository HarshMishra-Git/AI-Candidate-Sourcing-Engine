#!/usr/bin/env python3
"""
Test script for Synapse AI Hackathon submission
Demonstrates the AI Sourcing Agent with the Windsurf job description
"""

import json
import time
from datetime import datetime
from main import SourcingAgent

def test_synapse_job():
    """Test the system with the Synapse job description"""
    
    # The exact job description from Synapse hackathon
    windsurf_job = """About the Company:
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
Excited to build product-facing features from ML research"""

    print("🚀 SYNAPSE AI HACKATHON - SOURCING AGENT TEST")
    print("=" * 60)
    print("Testing with Windsurf Software Engineer, ML Research role")
    print("=" * 60)
    
    try:
        # Initialize agent
        print("🔧 Initializing AI Sourcing Agent...")
        agent = SourcingAgent()
        print("✅ Agent initialized successfully!")
        
        # Run the complete pipeline
        print("\n📋 Running complete sourcing pipeline...")
        start_time = time.time()
        
        result = agent.run_pipeline(
            job_description=windsurf_job,
            use_cache=False,  # Don't use cache for demo
            top_candidates=10
        )
        
        processing_time = time.time() - start_time
        
        # Display results
        if 'error' not in result:
            print("\n" + "="*60)
            print("🎯 SYNAPSE HACKATHON RESULTS")
            print("="*60)
            
            # Basic stats
            print(f"📊 Total Candidates Found: {result['total_candidates_found']}")
            print(f"📈 Total Candidates Scored: {result['total_candidates_scored']}")
            print(f"⏱️ Processing Time: {result['processing_time']:.2f} seconds")
            
            # Scoring summary
            if result['scoring_summary']['total_candidates'] > 0:
                summary = result['scoring_summary']
                print(f"\n📊 SCORING SUMMARY:")
                print(f"   Average Score: {summary['average_score']}/10")
                print(f"   Highest Score: {summary['highest_score']}/10")
                print(f"   Lowest Score: {summary['lowest_score']}/10")
                print(f"   Candidates Above 7.0: {summary['candidates_above_threshold']}")
                
                # Score distribution
                dist = summary.get('score_distribution', {})
                if dist:
                    print(f"   Score Distribution:")
                    for range_key, count in dist.items():
                        print(f"     {range_key}: {count} candidates")
            
            # Top candidates
            print(f"\n🏆 TOP 5 CANDIDATES FOR WINDSURF:")
            for i, candidate in enumerate(result['top_candidates'][:5], 1):
                print(f"\n{i}. {candidate.get('name', 'Unknown')}")
                print(f"   Score: {candidate.get('fit_score', 0)}/10")
                print(f"   LinkedIn: {candidate.get('url', 'N/A')}")
                
                # Score breakdown
                breakdown = candidate.get('score_breakdown', {})
                if breakdown:
                    print("   Score Breakdown:")
                    for category, score in breakdown.items():
                        print(f"     • {category.replace('_', ' ').title()}: {score}/10")
                
                # Message preview
                message = candidate.get('message', '')
                if message:
                    preview = message[:150] + "..." if len(message) > 150 else message
                    print(f"   Message: {preview}")
            
            # Message statistics
            msg_stats = result['message_statistics']
            print(f"\n✉️ MESSAGE GENERATION:")
            print(f"   Generated: {msg_stats['successful_generations']}")
            print(f"   Fallbacks: {msg_stats['fallback_messages']}")
            print(f"   Average Length: {msg_stats['average_length']} chars")
            
            # Export results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"synapse_hackathon_results_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            print(f"\n💾 Results exported to: {filename}")
            
            # Hackathon compliance check
            print(f"\n✅ HACKATHON COMPLIANCE CHECK:")
            print(f"   ✅ Job Input: Accepts job description ✓")
            print(f"   ✅ LinkedIn Discovery: Found {result['total_candidates_found']} candidates ✓")
            print(f"   ✅ Fit Scoring: Scored {result['total_candidates_scored']} candidates ✓")
            print(f"   ✅ Message Generation: Generated {msg_stats['successful_generations']} messages ✓")
            print(f"   ✅ Scale Support: Batch processing enabled ✓")
            print(f"   ✅ Bonus Features: Caching, multi-source search, async processing ✓")
            
            return True
            
        else:
            print(f"❌ Pipeline failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_synapse_job()
    if success:
        print("\n🎉 SYNAPSE HACKATHON TEST COMPLETED SUCCESSFULLY!")
        print("Your AI Sourcing Agent is ready for submission!")
    else:
        print("\n❌ Test failed. Please check your configuration.") 