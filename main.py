#!/usr/bin/env python3
"""
AI-Powered Recruitment Sourcing Agent
Main orchestrator script for the recruitment pipeline
"""

import json
import time
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from config import get_config, validate_config
from groq_utils import GroqClient
from search import LinkedInSearcher
from score import CandidateScorer
from message import MessageGenerator

class SourcingAgent:
    def __init__(self):
        """Initialize the sourcing agent with all components"""
        self.config = get_config()
        
        # Validate configuration
        if not validate_config():
            raise ValueError("Invalid configuration. Please check your environment variables.")
        
        # Initialize components
        self.groq_client = GroqClient()
        self.searcher = LinkedInSearcher()
        self.scorer = CandidateScorer(self.groq_client)
        self.message_generator = MessageGenerator(self.groq_client)
        
        # Cache management
        self.cache_file = self.config["cache_file"]
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file"""
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
                
                # Clean expired entries
                current_time = datetime.now()
                expiry_hours = self.config["cache_expiry_hours"]
                
                valid_cache = {}
                for key, entry in cache_data.items():
                    if 'timestamp' in entry:
                        entry_time = datetime.fromisoformat(entry['timestamp'])
                        if current_time - entry_time < timedelta(hours=expiry_hours):
                            valid_cache[key] = entry
                
                return valid_cache
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2, default=str)
        except Exception as e:
            print(f"Failed to save cache: {e}")
    
    def _get_cache_key(self, job_description: str) -> str:
        """Generate cache key for job description"""
        import hashlib
        return hashlib.md5(job_description.encode()).hexdigest()
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if results are cached and valid"""
        return cache_key in self.cache
    
    def run_pipeline(self, job_description: str, use_cache: bool = False, top_candidates: int = 10) -> Dict[str, Any]:
        """Run the complete sourcing pipeline"""
        start_time = time.time()
        
        print("="*60)
        print("🚀 Starting AI Sourcing Agent Pipeline")
        print("="*60)
        print(f"Job Description: {job_description[:100]}...")
        print(f"Target Candidates: {top_candidates}")
        print()
        
        # Check cache
        cache_key = self._get_cache_key(job_description)
        if use_cache and self._is_cached(cache_key):
            print("📂 Found cached results, returning cached data...")
            cached_result = self.cache[cache_key]['result']
            cached_result['from_cache'] = True
            return cached_result
        
        try:
            # Step 1: Extract job requirements
            print("📋 Step 1: Analyzing job description...")
            job_requirements = self.groq_client.extract_job_requirements(job_description)
            if job_requirements:
                print(f"   ✓ Extracted requirements: {job_requirements.get('title', 'N/A')}")
            else:
                print("   ⚠ Failed to extract structured requirements, using fallback")
            
            # Step 2: Search for candidates
            print("\n🔍 Step 2: Searching for LinkedIn candidates...")
            candidates = self.searcher.search_candidates(job_description, job_requirements or {})
            
            if not candidates:
                return {
                    'error': 'No candidates found',
                    'job_description': job_description,
                    'timestamp': datetime.now().isoformat(),
                    'processing_time': time.time() - start_time
                }
            
            print(f"   ✓ Found {len(candidates)} potential candidates")
            
            # Step 3: Score candidates
            print("\n📊 Step 3: Scoring candidates using AI...")
            scored_candidates = self.scorer.score_candidates_batch(job_description, candidates)
            
            # Step 4: Generate messages for top candidates
            print(f"\n✉️ Step 4: Generating personalized messages...")
            top_scored = self.scorer.get_top_candidates(scored_candidates, top_candidates)
            final_candidates = self.message_generator.generate_messages_batch(job_description, top_scored)
            
            # Step 5: Compile results
            print("\n📈 Step 5: Compiling results...")
            
            scoring_summary = self.scorer.get_scoring_summary(scored_candidates)
            message_stats = self.message_generator.get_message_statistics(final_candidates)
            
            result = {
                'job_description': job_description,
                'job_requirements': job_requirements,
                'top_candidates': final_candidates,
                'total_candidates_found': len(candidates),
                'total_candidates_scored': len(scored_candidates),
                'scoring_summary': scoring_summary,
                'message_statistics': message_stats,
                'timestamp': datetime.now().isoformat(),
                'processing_time': round(time.time() - start_time, 2),
                'from_cache': False
            }
            
            # Cache the result
            self.cache[cache_key] = {
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            self._save_cache()
            
            # Print summary
            self._print_summary(result)
            
            return result
            
        except Exception as e:
            error_result = {
                'error': str(e),
                'job_description': job_description,
                'timestamp': datetime.now().isoformat(),
                'processing_time': time.time() - start_time
            }
            print(f"\n❌ Pipeline failed: {e}")
            return error_result
    
    def _print_summary(self, result: Dict[str, Any]):
        """Print pipeline execution summary"""
        print("\n" + "="*60)
        print("📊 PIPELINE SUMMARY")
        print("="*60)
        
        print(f"Total Processing Time: {result['processing_time']} seconds")
        print(f"Candidates Found: {result['total_candidates_found']}")
        print(f"Candidates Scored: {result['total_candidates_scored']}")
        print(f"Top Candidates Returned: {len(result['top_candidates'])}")
        
        if result['scoring_summary']['total_candidates'] > 0:
            summary = result['scoring_summary']
            print(f"Average Score: {summary['average_score']}/10")
            print(f"Highest Score: {summary['highest_score']}/10")
            print(f"Candidates Above 7.0: {summary['candidates_above_threshold']}")
        
        print("\n🏆 TOP 3 CANDIDATES:")
        for i, candidate in enumerate(result['top_candidates'][:3], 1):
            print(f"{i}. {candidate.get('name', 'Unknown')} - Score: {candidate.get('fit_score', 0)}/10")
        
        print("\n✉️ MESSAGE GENERATION:")
        msg_stats = result['message_statistics']
        print(f"Messages Generated: {msg_stats['successful_generations']}")
        print(f"Fallback Messages: {msg_stats['fallback_messages']}")
        print(f"Average Length: {msg_stats['average_length']} characters")
        
        print("\n" + "="*60)
    
    async def run_pipeline_async(self, job_description: str, use_cache: bool = True, top_candidates: int = 10) -> Dict[str, Any]:
        """Async version of pipeline for better performance"""
        # For now, run the sync version in executor
        # Could be enhanced with true async support
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.run_pipeline, 
            job_description, 
            use_cache, 
            top_candidates
        )
    
    def export_results(self, result: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Export results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sourcing_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            print(f"📁 Results exported to: {filename}")
            return filename
        except Exception as e:
            print(f"Failed to export results: {e}")
            return ""
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache = {}
        self._save_cache()
        print("🗑️ Cache cleared")
    
    def run_batch_jobs(self, job_descriptions: list, use_cache: bool = True, top_candidates: int = 10) -> list:
        """Run the sourcing pipeline for multiple jobs in parallel (batch processing)"""
        import concurrent.futures
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(5, len(job_descriptions))) as executor:
            future_to_job = {
                executor.submit(self.run_pipeline, jd, use_cache, top_candidates): jd
                for jd in job_descriptions
            }
            for future in concurrent.futures.as_completed(future_to_job):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({'error': str(e), 'job_description': future_to_job[future]})
        return results

def main():
    """Main function for command line usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python main.py 'job description'")
        print("Example: python main.py 'Software Engineer, ML Research at Windsurf (Codeium)'")
        return
    
    job_description = ' '.join(sys.argv[1:])
    
    try:
        agent = SourcingAgent()
        result = agent.run_pipeline(job_description)
        
        # Export results
        agent.export_results(result)
        
        print("\n✅ Pipeline completed successfully!")
        
    except Exception as e:
        print(f"❌ Failed to run pipeline: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
