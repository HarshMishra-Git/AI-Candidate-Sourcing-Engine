import time
import asyncio
import concurrent.futures
from typing import List, Dict, Any, Optional
import json
from groq_utils import GroqClient
from config import get_config

class CandidateScorer:
    def __init__(self, groq_client: Optional[GroqClient] = None):
        """Initialize candidate scorer with Groq client"""
        self.groq_client = groq_client or GroqClient()
        self.config = get_config()
        self.scoring_rubric = self.config["scoring_rubric"]

    def calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted overall score based on rubric"""
        total_score = 0.0
        total_weight = 0.0

        for category, weight in self.scoring_rubric.items():
            if category in scores:
                total_score += scores[category] * weight
                total_weight += weight

        return round(total_score / total_weight if total_weight > 0 else 0.0, 1)

    def score_single_candidate(self, job_description: str, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Score a single candidate using AI"""

        messages = [
            {
                "role": "system",
                "content": f"""You are an expert technical recruiter. Score candidates on a scale of 1-10 for each criterion.

IMPORTANT: Return ONLY valid JSON, no explanatory text before or after.

Required JSON structure:
{{
    "education": 8,
    "career_trajectory": 7,
    "company_relevance": 6,
    "experience_match": 9,
    "location_match": 5,
    "tenure": 7,
    "reasoning": "Brief explanation of the scores"
}}

Scoring guidelines:
- education (1-10): Educational background relevance to role
- career_trajectory (1-10): Career progression and growth
- company_relevance (1-10): Previous companies' relevance to target role
- experience_match (1-10): Technical skills and experience alignment
- location_match (1-10): Geographic compatibility (10 for remote/flexible)
- tenure (1-10): Job stability and appropriate tenure lengths (not too short, not too long)

Score conservatively. Average candidates should score 5-6, good candidates 7-8, exceptional candidates 9-10."""
            },
            {
                "role": "user",
                "content": f"""Score this candidate against the job requirements:

JOB DESCRIPTION:
{job_description[:2000]}

CANDIDATE PROFILE:
Name: {candidate.get('name', 'Unknown')}
LinkedIn: {candidate.get('url', 'N/A')}
Profile Text: {candidate.get('profile_text', 'No profile text available')[:1500]}
Profile Snippet: {candidate.get('snippet', 'No snippet available')}

Provide scores and brief reasoning."""
            }
        ]

        response = self.groq_client.make_request(messages)
        if not response:
            print(f"No response received for candidate: {candidate.get('name', 'Unknown')}")
            return self._create_fallback_score(candidate, "API request failed - no response")

        try:
            # Log the raw response
            print(f"Raw Groq response for {candidate.get('name', 'Unknown')}: {response[:500]}")
            # Clean and parse JSON
            cleaned_response = self.groq_client.clean_json_response(response)
            print(f"Cleaned response: {cleaned_response}")
            scores = json.loads(cleaned_response)

            # Validate and sanitize scores
            required_fields = ["education", "career_trajectory", "company_relevance", 
                             "experience_match", "location_match", "tenure"]

            sanitized_scores = {}
            for field in required_fields:
                raw_score = scores.get(field, 5)
                # Convert to int and clamp between 1-10
                try:
                    sanitized_scores[field] = max(1, min(10, int(float(raw_score))))
                except (ValueError, TypeError):
                    sanitized_scores[field] = 5

            # Calculate weighted total score
            total_score = sum(sanitized_scores[criterion] * weight 
                            for criterion, weight in self.scoring_rubric.items() 
                            if criterion in sanitized_scores)

            return {
                "fit_score": round(total_score, 2),
                "score_breakdown": sanitized_scores,
                "reasoning": scores.get("reasoning", "No reasoning provided")[:500]  # Limit reasoning length
            }

        except json.JSONDecodeError as e:
            print(f"JSON decode error for candidate {candidate.get('name', 'Unknown')}: {e}")
            print(f"Raw response: {response[:200]}...")
            return self._create_fallback_score(candidate, f"JSON parsing error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error scoring candidate {candidate.get('name', 'Unknown')}: {e}")
            return self._create_fallback_score(candidate, f"Scoring error: {str(e)}")

    def _create_fallback_score(self, candidate: Dict[str, Any], error_message: str = "") -> Dict[str, Any]:
        """Create fallback score when API fails, with error message"""
        candidate_result = candidate.copy()
        candidate_result.update({
            'fit_score': 0.0,
            'score_breakdown': {
                'education': 0,
                'career_trajectory': 0,
                'company_relevance': 0,
                'experience_match': 0,
                'location_match': 0,
                'tenure': 0
            },
            'reasoning': f'Failed to score candidate due to API error: {error_message}',
            'error': True
        })
        print(f"Fallback score for {candidate.get('name', 'Unknown')}: {error_message}")
        return candidate_result

    def score_candidates_batch(self, job_description: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score multiple candidates with rate limiting"""
        if not candidates:
            return []

        print(f"Scoring {len(candidates)} candidates...")

        scored_candidates = []

        # Process candidates sequentially to avoid rate limiting
        for i, candidate in enumerate(candidates):
            try:
                scored_candidate = self.score_single_candidate(job_description, candidate)
                scored_candidates.append(scored_candidate)
                print(f"Scored: {scored_candidate.get('name', 'Unknown')} - Score: {scored_candidate.get('fit_score', 0)}")

                # Add delay between requests to prevent rate limiting
                if i < len(candidates) - 1:  # Don't sleep after the last candidate
                    time.sleep(1.5)  # 1.5 second delay between API calls

            except Exception as e:
                print(f"Failed to score candidate {candidate.get('name', 'Unknown')}: {e}")
                scored_candidates.append(self._create_fallback_score(candidate, f"Batch scoring error: {str(e)}"))

        # Sort by fit score (highest first)
        scored_candidates.sort(key=lambda x: x.get('fit_score', 0), reverse=True)

        print(f"Completed scoring {len(scored_candidates)} candidates")
        return scored_candidates

    async def score_candidates_async(self, job_description: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Async version of candidate scoring"""
        loop = asyncio.get_event_loop()

        # Run the synchronous scoring in thread pool
        return await loop.run_in_executor(
            None, 
            self.score_candidates_batch, 
            job_description, 
            candidates
        )

    def get_top_candidates(self, scored_candidates: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
        """Get top N candidates by score"""
        return sorted(scored_candidates, key=lambda x: x.get('fit_score', 0), reverse=True)[:top_n]

    def filter_candidates_by_score(self, scored_candidates: List[Dict[str, Any]], min_score: float = 5.0) -> List[Dict[str, Any]]:
        """Filter candidates by minimum score threshold"""
        return [candidate for candidate in scored_candidates if candidate.get('fit_score', 0) >= min_score]

    def get_scoring_summary(self, scored_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for scored candidates"""
        if not scored_candidates:
            return {
                'total_candidates': 0,
                'average_score': 0.0,
                'highest_score': 0.0,
                'lowest_score': 0.0,
                'candidates_above_threshold': 0
            }

        scores = [candidate.get('fit_score', 0) for candidate in scored_candidates]

        return {
            'total_candidates': len(scored_candidates),
            'average_score': round(sum(scores) / len(scores), 1),
            'highest_score': max(scores),
            'lowest_score': min(scores),
            'candidates_above_threshold': len([s for s in scores if s >= 7.0]),
            'score_distribution': {
                '8-10': len([s for s in scores if s >= 8.0]),
                '6-8': len([s for s in scores if 6.0 <= s < 8.0]),
                '4-6': len([s for s in scores if 4.0 <= s < 6.0]),
                '0-4': len([s for s in scores if s < 4.0])
            }
        }