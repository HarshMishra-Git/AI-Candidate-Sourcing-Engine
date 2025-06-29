import json
import re
import requests
import time
from typing import Dict, Any, Optional, List
from config import get_config

class GroqClient:
    def __init__(self, api_key: str = None, model: str = None):
        """Initialize Groq client with API key and model"""
        config = get_config()
        self.api_key = api_key or config["groq_api_key"]
        self.base_url = config["groq_base_url"]
        self.model = model or config["default_model"]
        self.alternative_model = config["alternative_model"]
        self.timeout = config["timeout_seconds"]
        self.max_retries = config["max_retries"]

        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable.")

    def clean_json_response(self, response_text: str) -> str:
        """Clean and extract JSON from AI model response"""
        # Remove common prefixes
        response_text = re.sub(r'^.*?(?=\{)', '', response_text, flags=re.DOTALL)

        # Remove common suffixes after JSON
        response_text = re.sub(r'\}.*$', '}', response_text, flags=re.DOTALL)

        # Try to find JSON objects or arrays
        json_match = re.search(r'(\{.*\}|\[.*\])', response_text, re.DOTALL)
        if json_match:
            return json_match.group(1)

        return response_text.strip()

    def _make_request(self, prompt: str, temperature: float = 0.7, model: str = None) -> Optional[str]:
        """Make a request to Groq API with improved retry logic"""
        current_model = model or self.model
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": current_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 1024,
            "top_p": 0.9
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url, 
                    headers=headers, 
                    json=payload, 
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        return data["choices"][0]["message"]["content"]
                    else:
                        print(f"Unexpected response format: {data}")
                        return None

                elif response.status_code == 429:  # Rate limit
                    wait_time = min(60, (2 ** attempt) + (attempt * 2))  # Exponential backoff with jitter
                    print(f"Rate limited. Waiting {wait_time} seconds before retry {attempt + 1}")
                    time.sleep(wait_time)

                elif response.status_code == 400:
                    error_data = response.json() if response.content else {}
                    error_message = error_data.get('error', {}).get('message', 'Unknown error')

                    if current_model == self.model and 'model' in error_message.lower():
                        # Try alternative model if primary fails
                        print(f"Model {current_model} failed ({error_message}), trying {self.alternative_model}")
                        current_model = self.alternative_model
                        payload["model"] = current_model
                        continue
                    else:
                        print(f"API request failed: {error_message}")
                        return None

                elif response.status_code == 401:
                    print(f"Authentication failed. Check API key.")
                    return None

                else:
                    print(f"API request failed with status {response.status_code}: {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)

            except requests.exceptions.Timeout:
                print(f"Request timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
            except requests.exceptions.RequestException as e:
                print(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)

        print(f"Failed to get response after {self.max_retries} attempts")
        return None

    def _clean_json_response(self, response: str) -> str:
        """Clean and extract JSON from response"""
        if not response:
            return ""

        response = response.strip()

        # Remove common prefixes
        prefixes_to_remove = [
            "Here is the JSON object with the scores:",
            "Here is the JSON object with scores:",
            "Based on the provided job description and candidate profile, I scored the candidate as follows:",
            "Here's the breakdown:",
            "```json",
            "```"
        ]

        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()

        # Find JSON object boundaries
        start_idx = response.find('{')
        if start_idx == -1:
            return ""

        # Find the matching closing brace
        brace_count = 0
        end_idx = -1
        for i in range(start_idx, len(response)):
            if response[i] == '{':
                brace_count += 1
            elif response[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break

        if end_idx == -1:
            return ""

        return response[start_idx:end_idx]

    def score_candidate(self, job_description: str, candidate_profile: str) -> Optional[Dict[str, Any]]:
        """Score a candidate using Groq LLM based on the rubric"""
        prompt = f"""
You must respond with ONLY a valid JSON object. No explanatory text before or after.

Job Description: {job_description}
Candidate Profile: {candidate_profile}

Rate this candidate 1-10 on each category and return this exact JSON format:

{{
    "education": 8,
    "career_trajectory": 7,
    "company_relevance": 6,
    "experience_match": 9,
    "location_match": 8,
    "tenure": 7,
    "overall_score": 7.5,
    "reasoning": "Brief explanation"
}}

IMPORTANT: Return ONLY the JSON object above. No other text.
"""

        response = self._make_request(prompt, temperature=0.1)
        if not response:
            return None

        try:
            # Clean and extract JSON
            clean_response = self._clean_json_response(response)
            if not clean_response:
                print(f"No valid JSON found in response: {response[:200]}...")
                return None

            score_data = json.loads(clean_response)

            # Validate required fields
            required_fields = ["education", "career_trajectory", "company_relevance", 
                             "experience_match", "location_match", "tenure"]

            if all(field in score_data for field in required_fields):
                return score_data
            else:
                print(f"Missing required fields in scoring response: {score_data}")
                return None

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Raw response: {response[:200]}...")
            print(f"Cleaned response: {self._clean_json_response(response)[:200]}...")
            return None

    def generate_message(self, job_description: str, candidate_profile: str, candidate_name: str) -> Optional[str]:
        """Generate personalized outreach message using Groq LLM"""
        prompt = f"""
Write a personalized LinkedIn outreach message for {candidate_name}. Be concise, professional, and specific. Maximum 120 words.

Job: {job_description}
Candidate: {candidate_name}
Profile: {candidate_profile}

Requirements:
- Address {candidate_name} by name
- Mention 1-2 specific aspects of their background
- Include clear call to action
- Professional but conversational tone

Return ONLY the message text without quotes or formatting.
"""

        response = self._make_request(prompt, temperature=0.6)
        if response:
            # Clean up the response
            response = response.strip()
            if response.startswith('"') and response.endswith('"'):
                response = response[1:-1]
            if response.startswith("Here is") or response.startswith("Here's"):
                # Remove common prefixes
                lines = response.split('\n')
                for i, line in enumerate(lines):
                    if line.strip() and not line.strip().startswith('Here'):
                        response = '\n'.join(lines[i:]).strip()
                        break
        return response

    def extract_job_requirements(self, job_description: str) -> Optional[Dict[str, Any]]:
        """Extract structured requirements from job description"""
        messages = [
            {
                "role": "system",
                "content": """You are an expert job analyst. Extract key requirements from job descriptions.

IMPORTANT: Return ONLY valid JSON, no explanatory text before or after.

Return a JSON object with these exact keys:
{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1", "skill2"],
  "experience_years": 3,
  "education_level": "Bachelor's",
  "location": "San Francisco, CA",
  "job_title": "Software Engineer",
  "company_type": "startup"
}"""
            },
            {
                "role": "user", 
                "content": f"Extract requirements from this job description:\n\n{job_description}"
            }
        ]

        response = self.make_request(messages)
        if not response:
            print("No response from API for job requirements extraction")
            return None

        try:
            cleaned_response = self.clean_json_response(response)
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            print(f"Failed to parse job requirements JSON: {e}")
            print(f"Raw response: {response}")
            # Return fallback structure
            return {
                "required_skills": [],
                "preferred_skills": [],
                "experience_years": 0,
                "education_level": "Bachelor's",
                "location": "Unknown",
                "job_title": "Unknown",
                "company_type": "Unknown"
            }

    def make_request(self, messages: List[Dict[str, str]], model: str = None) -> Optional[str]:
        """Make a request to Groq API with retry logic and exponential backoff"""
        model = model or self.model

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 1500,
            "top_p": 0.9
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        for attempt in range(self.max_retries):
            try:
                # Exponential backoff with jitter
                if attempt > 0:
                    wait_time = (2 ** attempt) + (attempt * 0.5)
                    print(f"Waiting {wait_time:.1f} seconds before retry {attempt + 1}...")
                    time.sleep(wait_time)

                response = requests.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    return self.clean_json_response(content)
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('retry-after', 60))
                    print(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                elif response.status_code >= 500:
                    print(f"Server error {response.status_code}. Retrying...")
                    continue
                else:
                    print(f"API request failed with status {response.status_code}: {response.text}")
                    # Try alternative model on client errors
                    if model == self.model and attempt < self.max_retries - 1:
                        model = self.alternative_model
                        print(f"Switching to alternative model: {model}")
                        continue

            except requests.exceptions.Timeout:
                print(f"Request timeout on attempt {attempt + 1}")
            except requests.exceptions.ConnectionError:
                print(f"Connection error on attempt {attempt + 1}")
            except requests.exceptions.RequestException as e:
                print(f"Request exception on attempt {attempt + 1}: {e}")
            except Exception as e:
                print(f"Unexpected error on attempt {attempt + 1}: {e}")

        print(f"All {self.max_retries} attempts failed for model {model}")
        return None