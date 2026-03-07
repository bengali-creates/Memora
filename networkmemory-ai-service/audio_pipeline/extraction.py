"""
Contact Information Extraction Module

The brain of the system - extracts structured data from unstructured conversation

Why Gemini 2.0 Flash:
1. FREE - 1500 requests/day
2. FAST - responses in 1-2 seconds
3. SMART - excellent at structured extraction
4. 1M context window - can handle very long conversations
5. JSON mode - reliably outputs valid JSON

This module is where PROMPT ENGINEERING matters most!
"""

import os
import json
import google.generativeai as genai
from typing import Dict, Optional
import time
from config import settings
from privacy_config import privacy_settings


class ContactExtractor:
    """
    Extracts structured contact information from conversations using Gemini

    Key challenges solved:
    1. Identifying who is USER vs CONTACT
    2. Extracting only mentioned information (no hallucination)
    3. Handling incomplete/missing data gracefully
    4. Calculating confidence scores
    """

    def __init__(self):
        """Initialize Gemini API"""
        api_key = settings.GEMINI_API_KEY

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Get one from https://makersuite.google.com/app/apikey"
            )

        genai.configure(api_key=api_key)

        # Use stable Gemini model
        # models/gemini-flash-latest is the most stable model name
        self.model = genai.GenerativeModel('models/gemini-flash-latest')

        print("[OK] Gemini initialized (model: gemini-pro)")

    def extract_contact(
        self,
        conversation_text: str,
        event_context: Optional[Dict[str, str]] = None,
        user_profile: Optional[Dict[str, any]] = None
    ) -> Dict:
        """
        Extract contact information from conversation

        Args:
            conversation_text: Diarized conversation
                               Format: "Speaker A: text\\nSpeaker B: text"
            event_context: Optional dict with event_name, location, timestamp
            user_profile: Optional dict with user's info (name, company, role, etc.)
                         Used to filter out the user's own information

        Returns:
            Dict with extracted contact information

        The Magic: The Prompt
        ----------------------
        This prompt took iteration to get right. Key insights:
        1. Be VERY specific about what to extract
        2. Emphasize "ONLY extract what's explicitly mentioned"
        3. Explain the difference between USER and CONTACT
        4. Use user_profile to filter out user's own info
        5. Request JSON directly (Gemini is good at this)
        6. Include examples in the prompt (few-shot learning)
        """
        print(f"\n[AI] Extracting contact information...")
        print(f"   Conversation length: {len(conversation_text)} characters")
        start_time = time.time()

        # Build context string
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
USER'S PROFILE (DO NOT EXTRACT THIS PERSON - THEY ARE THE APP USER):
- Name: {user_profile.get('name', 'Unknown')}
- Role: {user_profile.get('role', 'Unknown')}
- Company: {user_profile.get('company', 'Unknown')}
- Location: {user_profile.get('location', 'Unknown')}
- Industry: {user_profile.get('industry', 'Unknown')}
- Expertise: {', '.join(user_profile.get('expertise', []))}
- Goals: {', '.join(user_profile.get('networkingGoals', []))}

CRITICAL: If you see information matching the above user profile, IGNORE IT.
Extract information about the OTHER person (the CONTACT) ONLY.
"""

        # THE PROMPT - This is the most important part!
        prompt = f"""You are an AI assistant that extracts contact information from networking conversations.

IMPORTANT CONTEXT:
In this conversation, there are TWO people:
1. The USER - the person using this app (they want to remember who they met)
2. The CONTACT - the other person they met (THIS is who we want to extract info about)

{user_profile_str}

YOUR TASK:
Extract information about the CONTACT (NOT the user).

{context_str}

CONVERSATION:
{conversation_text}

EXTRACTION RULES:
1. Extract ONLY information explicitly mentioned in the conversation
2. DO NOT infer or guess information
3. If the CONTACT's name is not mentioned, try to use any identifying information
4. For topics_discussed: Be specific (e.g., "AI safety", "startup fundraising") not generic (e.g., "technology")
5. For follow_ups: Extract specific promises or action items mentioned
6. confidence_score should be:
   - 0.9-1.0: Name + multiple other fields present
   - 0.7-0.9: Name present, some other info
   - 0.5-0.7: Name present but limited info
   - 0.3-0.5: No name but some identifying info
   - 0.0-0.3: Very little useful information

EXTRACT THESE FIELDS:

{{
  "name": "Full name of the CONTACT (string or null if not mentioned)",
  "role": "Their job title OR student year (e.g., '2nd Year Student', 'Final Year') if they're a student",
  "company": "Company/organization OR university name if they're a student (e.g., 'Ali University', 'IIT Delhi')",
  "location": "City/region they're from (string or null)",
  "phone": "Phone number if mentioned (string or null)",
  "email": "Email address if mentioned (string or null)",
  "linkedin_url": "LinkedIn URL if mentioned (string or null)",
  "topics_discussed": ["array", "of", "specific", "topics"],
  "follow_ups": ["array", "of", "action", "items"],
  "conversation_summary": "Brief 2-3 sentence summary focusing on what makes this person interesting/memorable",
  "confidence_score": 0.85
}}

EXAMPLES:

Example 1 - Good extraction:
Conversation: "Speaker A: Hi I'm John. Speaker B: Hey! I'm Sarah Chen, ML Engineer at Google. Speaker A: Cool! What do you work on? Speaker B: AI safety, specifically LLM alignment. Speaker A: Fascinating. Can you send me some papers? Speaker B: Sure, I'll connect with you on LinkedIn."

Output:
{{
  "name": "Sarah Chen",
  "role": "ML Engineer",
  "company": "Google",
  "location": null,
  "phone": null,
  "email": null,
  "linkedin_url": null,
  "topics_discussed": ["AI safety", "LLM alignment"],
  "follow_ups": ["Send research papers", "Connect on LinkedIn"],
  "conversation_summary": "Sarah is an ML Engineer at Google working on AI safety, specifically LLM alignment. She offered to share research papers and connect on LinkedIn.",
  "confidence_score": 0.9
}}

Example 2 - Missing name:
Conversation: "Speaker A: What brings you here? Speaker B: I work on blockchain stuff at a startup in SF. Speaker A: Which one? Speaker B: Can't say yet, we're in stealth. But happy to chat about crypto."

Output:
{{
  "name": null,
  "role": "Engineer",
  "company": "Stealth startup",
  "location": "San Francisco",
  "phone": null,
  "email": null,
  "linkedin_url": null,
  "topics_discussed": ["Blockchain", "Cryptocurrency", "Stealth startup"],
  "follow_ups": [],
  "conversation_summary": "Works on blockchain technology at a stealth mode startup in San Francisco. Open to discussing cryptocurrency.",
  "confidence_score": 0.45
}}

Example 3 - Student (University = Company):
Conversation: "Speaker A: Hi, what do you do? Speaker B: I'm Dev, I'm in my second year at Ali University. I'm diving into Web3 and blockchain stuff. Speaker A: Nice! What batch? Speaker B: 2028 batch, graduating in 2028."

Output:
{{
  "name": "Dev",
  "role": "2nd Year Student",
  "company": "Ali University",
  "location": null,
  "phone": null,
  "email": null,
  "linkedin_url": null,
  "topics_discussed": ["Web3", "Blockchain"],
  "follow_ups": ["Connect after graduation in 2028"],
  "conversation_summary": "Dev is a second-year student at Ali University (2028 batch) interested in Web3 and blockchain technology.",
  "confidence_score": 0.85
}}

NOW EXTRACT FROM THE CONVERSATION ABOVE.

RETURN ONLY VALID JSON (no markdown, no code blocks, no explanations, just raw JSON):
"""

        try:
            # Generate extraction
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean response (remove markdown if present)
            # Sometimes Gemini wraps JSON in ```json ... ```
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()

            # Parse JSON
            try:
                contact_card = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"[WARNING]  JSON parse error, trying to fix...")
                # Sometimes there's extra text before/after JSON
                # Try to extract just the JSON part
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    contact_card = json.loads(json_match.group())
                else:
                    raise Exception(f"Could not parse JSON from response: {response_text[:200]}")

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
            print(f"[ERROR] Extraction failed: {str(e)}")
            raise


# ============================================
# Test Function
# ============================================

def test_extraction():
    """
    Test extraction with sample conversations

    To run: python -m audio_pipeline.extraction
    """
    print("\n🧪 Testing Contact Extraction\n")

    extractor = ContactExtractor()

    # Test Case 1: Complete information
    print("\n" + "="*70)
    print("TEST 1: Complete information")
    print("="*70)

    sample_conversation_1 = """Speaker A: Hi! I'm John. Nice to meet you at DevFest!
Speaker B: Hey John! I'm Sarah Chen. Great to be here.
Speaker A: So Sarah, what do you do?
Speaker B: I'm a Machine Learning Engineer at Google. I work on the AI safety team in Mountain View.
Speaker A: That's amazing! I'm really interested in AI safety. What kind of problems are you working on?
Speaker B: We're focusing on alignment and interpretability. Making sure LLMs behave as intended.
Speaker A: Fascinating. I'm working on a startup in the AI space. Would love to learn more.
Speaker B: Definitely! Let's connect on LinkedIn. I can also send you some papers we've published.
Speaker A: That would be great. I'll send you a connection request today.
Speaker B: Sounds good! Also, if you're interested, we're hiring. I can refer you."""

    event_context_1 = {
        "event_name": "DevFest Kolkata 2026",
        "location": "Kolkata",
        "timestamp": "2026-03-04T15:30:00Z"
    }

    try:
        result_1 = extractor.extract_contact(sample_conversation_1, event_context_1)
        print(f"\n[OK] Test 1 Successful!")
        print(f"\n📇 Contact Card:")
        print(json.dumps(result_1, indent=2))
    except Exception as e:
        print(f"\n[ERROR] Test 1 failed: {e}")

    # Test Case 2: Missing information
    print("\n" + "="*70)
    print("TEST 2: Incomplete information (missing name)")
    print("="*70)

    sample_conversation_2 = """Speaker A: What brings you here?
Speaker B: I work on blockchain stuff at a startup in San Francisco.
Speaker A: Which startup?
Speaker B: Can't say yet, we're in stealth mode. But happy to chat about crypto!
Speaker A: Cool, what aspect of blockchain?
Speaker B: Smart contracts and DeFi protocols mainly. Working on making them more secure.
Speaker A: Interesting. How long have you been in SF?
Speaker B: About 2 years now. Moved from New York."""

    event_context_2 = {
        "event_name": "TechCrunch Disrupt 2026",
        "location": "San Francisco",
        "timestamp": "2026-03-05T10:00:00Z"
    }

    try:
        result_2 = extractor.extract_contact(sample_conversation_2, event_context_2)
        print(f"\n[OK] Test 2 Successful!")
        print(f"\n📇 Contact Card:")
        print(json.dumps(result_2, indent=2))
    except Exception as e:
        print(f"\n[ERROR] Test 2 failed: {e}")


if __name__ == "__main__":
    test_extraction()
