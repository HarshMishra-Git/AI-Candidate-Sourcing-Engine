import concurrent.futures
from typing import List, Dict, Any, Optional
from groq_utils import GroqClient
from config import get_config
import time

class MessageGenerator:
    def __init__(self, groq_client: Optional[GroqClient] = None):
        """Initialize message generator with Groq client"""
        self.groq_client = groq_client or GroqClient()
        self.config = get_config()

    def generate_single_message(self, job_description: str, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized message for a single candidate"""
        job_description = job_description or ""
        try:
            candidate_name = candidate.get('name', 'there')
            profile_text = candidate.get('profile_text', '')

            # If no profile text, use basic info
            if not profile_text:
                profile_text = f"LinkedIn profile: {candidate.get('url', 'N/A')}"

            # Generate message using Groq
            message = self.generate_message(
                job_description=job_description or "",
                candidate=candidate
            )

            if message:
                # Update candidate with message
                candidate_result = candidate.copy()
                candidate_result['message'] = message.strip()
                candidate_result['message_generated'] = True

                return candidate_result
            else:
                print(f"Failed to generate message for: {candidate_name}")
                return self._create_fallback_message(candidate, job_description or "")

        except Exception as e:
            print(f"Error generating message for {candidate.get('name', 'Unknown')}: {e}")
            return self._create_fallback_message(candidate, job_description or "")

    def _create_fallback_message(self, candidate: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Create fallback message when API fails"""
        job_description = job_description or ""
        candidate_name = candidate.get('name', 'there')
        # Extract job title from description (simple heuristic)
        job_desc = job_description or "this position"
        job_lines = job_desc.split('\n')
        job_title = job_lines[0] if job_lines else 'this position'
        fallback_message = f"""Hi {candidate_name},

I hope this message finds you well. I came across your LinkedIn profile and was impressed by your background and experience.

We have an exciting opportunity for {job_title} that I believe could be a great fit for your skills and career goals. I'd love to discuss this role with you and learn more about your interests.

Would you be open to a brief conversation this week? I'd be happy to share more details about the position and our team.

Best regards"""
        candidate_result = candidate.copy()
        candidate_result.update({
            'message': fallback_message,
            'message_generated': True,
            'fallback_message': True
        })
        return candidate_result

    def generate_messages_batch(self, job_description: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate messages for multiple candidates with rate limiting"""
        if not candidates:
            return []

        print(f"Generating messages for {len(candidates)} candidates...")

        candidates_with_messages = []
        batch_size = self.config["batch_size"]

        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            # Submit all message generation tasks
            future_to_candidate = {
                executor.submit(self.generate_single_message, job_description, candidate): candidate
                for candidate in candidates
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_candidate):
                try:
                    candidate_with_message = future.result()
                    candidates_with_messages.append(candidate_with_message)
                    print(f"Generated message for: {candidate_with_message.get('name', 'Unknown')}")
                except Exception as e:
                    candidate = future_to_candidate[future]
                    print(f"Failed to generate message for {candidate.get('name', 'Unknown')}: {e}")
                    candidates_with_messages.append(self._create_fallback_message(candidate, job_description))

        print(f"Completed message generation for {len(candidates_with_messages)} candidates")
        return candidates_with_messages

    def customize_message_tone(self, message: str, tone: str = "professional") -> str:
        """Customize message tone (professional, casual, enthusiastic)"""
        # This could be enhanced with additional Groq calls for tone adjustment
        if tone == "casual":
            message = message.replace("I hope this message finds you well.", "Hope you're doing well!")
            message = message.replace("Best regards", "Cheers")
        elif tone == "enthusiastic":
            message = message.replace("exciting opportunity", "amazing opportunity")
            message = message.replace("I'd love to", "I'm excited to")

        return message

    def add_company_signature(self, message: str, company_name: Optional[str] = None, recruiter_name: Optional[str] = None) -> str:

        """Add company signature to message"""
        signature_parts = []

        if recruiter_name:
            signature_parts.append(recruiter_name)

        if company_name:
            signature_parts.append(company_name)

        if signature_parts:
            signature = "\n\n" + " | ".join(signature_parts)
            return message + signature

        return message

    def validate_message_length(self, message: str, max_length: int = 300) -> bool:
        """Validate message length for LinkedIn limits"""
        return len(message) <= max_length

    def get_message_statistics(self, candidates_with_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about generated messages"""
        if not candidates_with_messages:
            return {
                'total_messages': 0,
                'successful_generations': 0,
                'fallback_messages': 0,
                'average_length': 0
            }

        messages = [candidate.get('message', '') for candidate in candidates_with_messages]
        fallback_count = len([candidate for candidate in candidates_with_messages 
                            if candidate.get('fallback_message', False)])

        return {
            'total_messages': len(messages),
            'successful_generations': len(messages) - fallback_count,
            'fallback_messages': fallback_count,
            'average_length': round(sum(len(msg) for msg in messages) / len(messages)),
            'messages_within_limit': len([msg for msg in messages if len(msg) <= 300])
        }
    
    def generate_message(self, job_description: str, candidate: Dict[str, Any]) -> str:
        """Generate a personalized outreach message for a candidate"""
        job_description = job_description or ""
        # Truncate inputs to prevent token limits
        job_desc_short = job_description[:1000] if job_description else "No job description available"
        profile_short = candidate.get('profile_text', '')[:800] if candidate.get('profile_text') else "No profile available"

        messages = [
            {
                "role": "system", 
                "content": """You are an expert recruiter writing personalized LinkedIn outreach messages.

IMPORTANT: Return ONLY the message text, no JSON, no quotes, no extra formatting.

Write a professional, personalized message that:
- Is 120-180 words
- Mentions 1-2 specific details from their background
- Explains why they might be interested in the role
- Has a friendly, professional tone
- Ends with a simple question or call-to-action
- Avoids overly promotional language

Start with \"Hi [Name],\" and write naturally."""
            },
            {
                "role": "user",
                "content": f"""Write a personalized LinkedIn message:

JOB: {job_desc_short}

CANDIDATE:
Name: {candidate.get('name', 'there')}
Background: {profile_short}
LinkedIn: {candidate.get('url', 'N/A')}

Write the message now:"""
            }
        ]

        response = self.groq_client.make_request(messages)

        if response:
            # Clean up the response - remove common AI response patterns
            message = response.strip()

            # Remove quotes if the entire message is wrapped in them
            if (message.startswith('"') and message.endswith('"')) or \
               (message.startswith("'") and message.endswith("'")):
                message = message[1:-1]

            # Remove "Here is the message:" type prefixes
            prefixes_to_remove = [
                "Here is the message:",
                "Here's the message:",
                "Message:",
                "LinkedIn message:",
                "Outreach message:"
            ]

            for prefix in prefixes_to_remove:
                if message.lower().startswith(prefix.lower()):
                    message = message[len(prefix):].strip()

            # Ensure message is reasonable length and quality
            if 50 <= len(message) <= 500 and "Hi " in message:
                return message
            else:
                print(f"Generated message quality check failed for {candidate.get('name', 'Unknown')}")
                return self._create_fallback_message_string(candidate, job_description or "")
        else:
            print(f"No response received for message generation for {candidate.get('name', 'Unknown')}")
            return self._create_fallback_message_string(candidate, job_description or "")

    def _create_fallback_message_string(self, candidate: Dict[str, Any], job_description: str) -> str:
        """Create fallback message string when API fails"""
        job_description = job_description or ""
        candidate_name = candidate.get('name', 'there')
        # Extract job title from description (simple heuristic)
        job_desc = job_description or "this position"
        job_lines = job_desc.split('\n')
        job_title = job_lines[0] if job_lines else 'this position'
        fallback_message = f"""Hi {candidate_name},

I hope this message finds you well. I came across your LinkedIn profile and was impressed by your background and experience.

We have an exciting opportunity for {job_title} that I believe could be a great fit for your skills and career goals. I'd love to discuss this role with you and learn more about your interests.

Would you be open to a brief conversation this week? I'd be happy to share more details about the position and our team.

Best regards"""
        return fallback_message