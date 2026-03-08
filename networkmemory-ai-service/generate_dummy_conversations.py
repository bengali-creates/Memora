"""
Generate dummy conversation data for mood detection model training

This script uses an LLM to generate realistic networking conversations
with mood labels for training a custom mood detection model.
"""

import json
from datetime import datetime, timedelta
import random

PROMPT_FOR_LLM = """
Generate a realistic networking conversation transcript at a tech conference.

Create a conversation between:
- Speaker 1 (You): A professional attending the conference
- Speaker 2 (Contact): Another attendee you just met

Requirements:
1. Conversation should be 1-3 minutes long (10-30 exchanges)
2. Include natural speech patterns (um, uh, you know, like)
3. Make it realistic - mix small talk with business discussion
4. The mood should match the conversation type: {conversation_type}

Conversation Type: {conversation_type}
Setting: {setting}

Output the conversation in this EXACT JSON format:
{{
  "speakers": {{
    "you": {{
      "name": "Your Name",
      "role": "Your Role",
      "company": "Your Company"
    }},
    "contact": {{
      "name": "Contact Name",
      "role": "Contact Role",
      "company": "Contact Company"
    }}
  }},
  "transcript": "You: Hi, I'm...\nContact: Hey! I'm...\n...",
  "mood_analysis": {{
    "contact_mood": "enthusiastic|neutral|reserved|stressed|excited|professional|friendly|cold",
    "contact_mood_confidence": 0.0-1.0,
    "your_mood": "same options",
    "your_mood_confidence": 0.0-1.0,
    "conversation_energy": "high|medium|low",
    "energy_score": 0.0-1.0,
    "sentiment_score": -1.0 to +1.0,
    "emotional_indicators": {{
      "excited_words": ["list", "of", "words"],
      "hesitation_words": ["list", "of", "words"],
      "agreement_phrases": ["list", "of", "phrases"]
    }},
    "engagement": {{
      "contact_engagement": 0-100,
      "your_engagement": 0-100
    }},
    "follow_up_likelihood": {{
      "will_followup": true/false,
      "confidence": 0.0-1.0,
      "reason": "why or why not"
    }}
  }}
}}

Make the conversation natural and realistic!
"""

CONVERSATION_TYPES = [
    {
        "type": "high_energy",
        "count": 5,
        "description": "Both excited about shared interests. Fast-paced, enthusiastic.",
        "moods": ["enthusiastic", "excited"],
        "energy": "high",
        "sentiment": 0.7
    },
    {
        "type": "professional_neutral",
        "count": 5,
        "description": "Polite but not super engaging. Information exchange.",
        "moods": ["professional", "neutral"],
        "energy": "medium",
        "sentiment": 0.3
    },
    {
        "type": "one_sided",
        "count": 3,
        "description": "You're engaged, they're not (or vice versa). Short responses.",
        "moods": ["reserved", "cold"],
        "energy": "low",
        "sentiment": 0.1
    },
    {
        "type": "stressed_rushed",
        "count": 3,
        "description": "One person is busy. Quick exchanges.",
        "moods": ["stressed", "professional"],
        "energy": "low",
        "sentiment": 0.2
    },
    {
        "type": "perfect_match",
        "count": 4,
        "description": "Great chemistry. Lots of mutual interest. Plans to follow up.",
        "moods": ["enthusiastic", "friendly"],
        "energy": "high",
        "sentiment": 0.9
    }
]

SETTINGS = [
    "main conference hall between sessions",
    "coffee break networking area",
    "lunch table at conference",
    "after-panel Q&A discussion",
    "evening networking reception",
    "workshop breakout session",
    "expo hall at vendor booth",
    "conference lounge area"
]


def generate_conversation_metadata(conv_type, index):
    """Generate metadata for a conversation"""
    base_date = datetime(2026, 3, 5, 9, 0, 0)
    time_offset = timedelta(hours=random.randint(0, 8), minutes=random.randint(0, 59))

    return {
        "conversation_id": f"conv_{conv_type['type']}_{index:03d}",
        "duration": random.randint(60, 180),
        "setting": random.choice(SETTINGS),
        "date": (base_date + time_offset).isoformat(),
        "conversation_type": conv_type["type"]
    }


def print_generation_instructions():
    """Print instructions for generating conversations"""

    print("=" * 80)
    print("DUMMY CONVERSATION DATA GENERATION INSTRUCTIONS")
    print("=" * 80)
    print()
    print("This script will help you generate 20 realistic conversation transcripts")
    print("with mood analysis labels for training a custom mood detection model.")
    print()
    print("STEPS TO GENERATE DATA:")
    print()
    print("1. Use ChatGPT, Claude, or Gemini with the prompts below")
    print("2. Copy each generated conversation JSON")
    print("3. Save all conversations to: conversation_training_data.json")
    print()
    print("=" * 80)
    print()

    all_conversations = []
    conv_index = 1

    for conv_type in CONVERSATION_TYPES:
        print(f"\n{'=' * 80}")
        print(f"CONVERSATION TYPE: {conv_type['type'].upper()}")
        print(f"Generate {conv_type['count']} conversations")
        print(f"Description: {conv_type['description']}")
        print(f"{'=' * 80}\n")

        for i in range(conv_type['count']):
            metadata = generate_conversation_metadata(conv_type, i + 1)

            print(f"\n--- Conversation {conv_index}/{sum(ct['count'] for ct in CONVERSATION_TYPES)} ---")
            print(f"ID: {metadata['conversation_id']}")
            print(f"Type: {conv_type['type']}")
            print(f"Setting: {metadata['setting']}")
            print()
            print("PROMPT TO USE:")
            print("-" * 80)

            prompt = PROMPT_FOR_LLM.format(
                conversation_type=conv_type['description'],
                setting=metadata['setting']
            )
            print(prompt)
            print("-" * 80)
            print()
            print("After generating, add this metadata to the JSON:")
            print(json.dumps(metadata, indent=2))
            print()
            print("=" * 80)

            # Template for output
            conversation_template = {
                "metadata": metadata,
                "speakers": {
                    "you": {
                        "name": "[Generated by LLM]",
                        "role": "[Generated by LLM]",
                        "company": "[Generated by LLM]"
                    },
                    "contact": {
                        "name": "[Generated by LLM]",
                        "role": "[Generated by LLM]",
                        "company": "[Generated by LLM]"
                    }
                },
                "transcript": "[Generated by LLM]",
                "mood_analysis": {
                    "contact_mood": f"{random.choice(conv_type['moods'])}",
                    "contact_mood_confidence": round(random.uniform(0.7, 0.95), 2),
                    "your_mood": "professional",
                    "your_mood_confidence": round(random.uniform(0.7, 0.95), 2),
                    "conversation_energy": conv_type['energy'],
                    "energy_score": round(random.uniform(0.6, 1.0) if conv_type['energy'] == 'high' else random.uniform(0.2, 0.6), 2),
                    "sentiment_score": round(conv_type['sentiment'] + random.uniform(-0.1, 0.1), 2),
                    "emotional_indicators": {
                        "excited_words": [],
                        "hesitation_words": [],
                        "agreement_phrases": []
                    },
                    "engagement": {
                        "contact_engagement": random.randint(50, 100) if conv_type['energy'] == 'high' else random.randint(20, 60),
                        "your_engagement": random.randint(60, 95)
                    },
                    "follow_up_likelihood": {
                        "will_followup": conv_type['sentiment'] > 0.5,
                        "confidence": round(random.uniform(0.6, 0.95), 2),
                        "reason": "[Generated by LLM]"
                    }
                }
            }

            all_conversations.append(conversation_template)
            conv_index += 1

    print("\n" + "=" * 80)
    print("FINAL STEP: Save all conversations to JSON file")
    print("=" * 80)
    print()
    print("File name: conversation_training_data.json")
    print("Format:")
    print(json.dumps(all_conversations[:1], indent=2))
    print("... (19 more conversations)")
    print()
    print("=" * 80)
    print("QUICK START ALTERNATIVE:")
    print("=" * 80)
    print()
    print("If you want to skip manual generation, use this single prompt with ChatGPT/Claude:")
    print()
    print(generate_batch_prompt())


def generate_batch_prompt():
    """Generate a single prompt to create all conversations at once"""

    prompt = """
Generate 20 realistic networking conversation transcripts for a tech conference.
Output as a JSON array with all conversations.

Create conversations with these distributions:
- 5 high energy (both excited, enthusiastic, fast-paced)
- 5 professional neutral (polite, information exchange)
- 3 one-sided (one person engaged, other not interested)
- 3 stressed/rushed (one person is busy)
- 4 perfect match (great chemistry, will definitely follow up)

Each conversation JSON should include:
{
  "conversation_id": "conv_XXX",
  "metadata": {
    "duration": 60-180 seconds,
    "setting": "conference location",
    "date": "2026-03-05T10:30:00",
    "conversation_type": "high_energy|professional_neutral|one_sided|stressed_rushed|perfect_match"
  },
  "speakers": {
    "you": {"name": "...", "role": "...", "company": "..."},
    "contact": {"name": "...", "role": "...", "company": "..."}
  },
  "transcript": "You: Hi!\\nContact: Hey!\\n...",
  "mood_analysis": {
    "contact_mood": "enthusiastic|neutral|reserved|stressed|excited|professional|friendly|cold",
    "contact_mood_confidence": 0.0-1.0,
    "your_mood": "same options",
    "your_mood_confidence": 0.0-1.0,
    "conversation_energy": "high|medium|low",
    "energy_score": 0.0-1.0,
    "sentiment_score": -1.0 to +1.0,
    "emotional_indicators": {
      "excited_words": ["amazing", "definitely"],
      "hesitation_words": ["maybe", "not sure"],
      "agreement_phrases": ["totally", "exactly"]
    },
    "engagement": {
      "contact_engagement": 0-100,
      "your_engagement": 0-100
    },
    "follow_up_likelihood": {
      "will_followup": true/false,
      "confidence": 0.0-1.0,
      "reason": "explanation"
    }
  }
}

Make conversations realistic with:
- Natural speech (um, uh, you know)
- Mix of small talk and business
- Real tech industry scenarios
- Diverse speakers (engineers, founders, investors, etc.)

Output as valid JSON array: [conversation1, conversation2, ...]
"""
    return prompt


if __name__ == "__main__":
    print_generation_instructions()

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. Copy the batch prompt above")
    print("2. Paste into ChatGPT/Claude/Gemini")
    print("3. Save output to: conversation_training_data.json")
    print("4. Run: python train_mood_model.py (coming next!)")
    print()
