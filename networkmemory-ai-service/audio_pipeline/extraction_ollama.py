"""
Contact Information Extraction Module - Ollama Version

Uses local Ollama LLM instead of Gemini API
100% private - no data leaves your machine

Models recommended:
- llama3:8b - Best accuracy (4GB VRAM)
- mistral:7b - Faster, good accuracy (4GB VRAM)
- phi3:3.8b - Very fast, smaller (2GB VRAM)
"""

import json
import time
import httpx
from typing import Dict, Optional
from config import settings
from privacy_config import privacy_settings


class OllamaContactExtractor:
    """
    Extracts structured contact information using local Ollama LLM

    Benefits over Gemini:
    - 100% local (no API calls)
    - No data logging by third parties
    - Unlimited requests (no rate limits)
    - No costs

    Trade-offs:
    - Slower than Gemini API (depends on hardware)
    - Requires good CPU/GPU
    - ~80-90% accuracy vs Gemini's 95%
    """

    def __init__(self, model: str = "llama3"):
        """
        Initialize Ollama client

        Args:
            model: Ollama model name (llama3, mistral, phi3)
        """
        self.model = model
        self.base_url = "http://localhost:11434"  # Ollama default port

        # Test connection
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                if self.model not in model_names and f"{self.model}:latest" not in model_names:
                    print(f"[WARNING] Model '{self.model}' not found. Available: {model_names}")
                    print(f"[INFO] Run: ollama pull {self.model}")
            print(f"[OK] Ollama initialized (model: {self.model})")
        except Exception as e:
            print(f"[WARNING] Could not connect to Ollama: {e}")
            print(f"[INFO] Make sure Ollama is running: https://ollama.com")

    def extract_contact(
        self,
        conversation_text: str,
        event_context: Optional[Dict[str, str]] = None,
        user_profile: Optional[Dict[str, any]] = None
    ) -> Dict:
        """
        Extract contact information from conversation using Ollama

        Args:
            conversation_text: Diarized conversation
            event_context: Optional event info
            user_profile: Optional user profile (to filter out user's info)

        Returns:
            Dict with extracted contact information
        """
        print(f"\n[AI] Extracting contact information with Ollama...")
        print(f"   Model: {self.model}")
        print(f"   Conversation length: {len(conversation_text)} characters")
        start_time = time.time()

        # Build context
        context_str = ""
        if event_context:
            context_str = f"""
Event Context:
- Event: {event_context.get('event_name', 'Unknown')}
- Location: {event_context.get('location', 'Unknown')}
- Date: {event_context.get('timestamp', 'Unknown')}
"""

        # Build user profile string
        user_profile_str = ""
        if user_profile:
            user_profile_str = f"""
USER'S PROFILE (DO NOT EXTRACT - THEY ARE THE APP USER):
- Name: {user_profile.get('name', 'Unknown')}
- Role: {user_profile.get('role', 'Unknown')}
- Company: {user_profile.get('company', 'Unknown')}

CRITICAL: Extract info about the OTHER person (the CONTACT) ONLY.
"""

        # Simplified prompt for local LLMs (they need more concise instructions)
        prompt = f"""Extract contact information from this conversation. Focus on the OTHER person (not the user).

{user_profile_str}

{context_str}

CONVERSATION:
{conversation_text}

Extract these fields in JSON format:
- name: Person's full name (or null)
- role: Job title or student year (e.g., "2nd Year Student")
- company: Company name or university
- location: City/region
- phone: Phone number (or null)
- email: Email (or null)
- linkedin_url: LinkedIn URL (or null)
- topics_discussed: Array of specific topics (e.g., ["AI", "Blockchain"])
- follow_ups: Array of action items mentioned
- conversation_summary: 2-3 sentence summary
- confidence_score: 0.0 to 1.0 (how confident you are)

RULES:
1. Only extract what's explicitly mentioned
2. Don't infer or guess
3. Use null for missing fields
4. Return ONLY valid JSON, no explanations

JSON:"""

        try:
            # Call Ollama API
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"  # Request JSON output
                },
                timeout=120.0  # Local models can be slow
            )

            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

            result = response.json()
            response_text = result.get("response", "").strip()

            # Parse JSON
            try:
                contact_card = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    contact_card = json.loads(json_match.group())
                else:
                    raise Exception(f"Could not parse JSON from Ollama: {response_text[:200]}")

            # Add metadata
            # PRIVACY: Only store raw conversation if explicitly enabled
            if privacy_settings.STORE_RAW_CONVERSATION:
                contact_card["raw_conversation"] = conversation_text
                if privacy_settings.LOG_PROCESSING_ACTIVITIES:
                    print(f"[PRIVACY] Including raw_conversation ({len(conversation_text)} chars)")
            else:
                if privacy_settings.LOG_PROCESSING_ACTIVITIES:
                    print(f"[PRIVACY] Excluding raw_conversation (privacy mode enabled)")

            if event_context:
                contact_card["met_at"] = event_context.get("event_name")
                contact_card["met_date"] = event_context.get("timestamp")
                contact_card["met_location"] = event_context.get("location")

            extraction_time = time.time() - start_time
            contact_card["extraction_time"] = extraction_time

            print(f"[OK] Extraction complete in {extraction_time:.2f}s")
            print(f"\n[CONTACT] Extracted Contact:")
            print(f"   Name: {contact_card.get('name', 'Unknown')}")
            print(f"   Role: {contact_card.get('role', 'Unknown')}")
            print(f"   Company: {contact_card.get('company', 'Unknown')}")
            print(f"   Topics: {', '.join(contact_card.get('topics_discussed', [])[:3])}")
            print(f"   Confidence: {contact_card.get('confidence_score', 0):.0%}")

            return contact_card

        except Exception as e:
            print(f"[ERROR] Ollama extraction failed: {str(e)}")
            raise


# ============================================
# Test Function
# ============================================

def test_ollama_extraction():
    """
    Test extraction with Ollama

    To run: python -m audio_pipeline.extraction_ollama
    """
    print("\n🧪 Testing Ollama Contact Extraction\n")

    extractor = OllamaContactExtractor(model="llama3")

    # Test conversation
    sample_conversation = """Speaker A: Hi! I'm John. Nice to meet you at DevFest!
Speaker B: Hey John! I'm Sarah Chen. Great to be here.
Speaker A: So Sarah, what do you do?
Speaker B: I'm a Machine Learning Engineer at Google. I work on the AI safety team in Mountain View.
Speaker A: That's amazing! I'm really interested in AI safety. What kind of problems are you working on?
Speaker B: We're focusing on alignment and interpretability. Making sure LLMs behave as intended.
Speaker A: Fascinating. I'm working on a startup in the AI space. Would love to learn more.
Speaker B: Definitely! Let's connect on LinkedIn. I can also send you some papers we've published."""

    event_context = {
        "event_name": "DevFest Kolkata 2026",
        "location": "Kolkata",
        "timestamp": "2026-03-04T15:30:00Z"
    }

    try:
        result = extractor.extract_contact(sample_conversation, event_context)
        print(f"\n[OK] Test Successful!")
        print(f"\n📇 Contact Card:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")


if __name__ == "__main__":
    test_ollama_extraction()
