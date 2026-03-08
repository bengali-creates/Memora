"""
Test pipeline with actual audio to see transcription
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_pipeline.pipeline import AudioPipeline


async def test_with_audio():
    print("\n" + "="*70)
    print("[TEST] TESTING PIPELINE WITH ACTUAL AUDIO")
    print("="*70)

    # Initialize pipeline
    print("\n[STEP 1] Initializing pipeline...")
    pipeline = AudioPipeline(debug=True)

    # Test audio URL (direct AssemblyAI sample)
    # This is a short news clip about wildfires (~30 seconds)
    test_audio_url = "https://storage.googleapis.com/assembly-ai/docs/samples/20230607_me_canadian_wildfires.mp3"

    print(f"\n[STEP 2] Processing audio...")
    print(f"URL: {test_audio_url}")

    try:
        # Process audio
        result = await pipeline.process_audio(test_audio_url)

        # Show results
        print("\n" + "="*70)
        print("[RESULT] PROCESSING COMPLETE")
        print("="*70)

        if result["status"] == "success":
            print(f"\n[OK] Status: SUCCESS")

            contact = result["contact_card"]
            print(f"\nContact Card:")
            print(f"  Name: {contact.get('name', 'N/A')}")
            print(f"  Company: {contact.get('company', 'N/A')}")
            print(f"  Role: {contact.get('role', 'N/A')}")
            print(f"  Confidence: {contact.get('confidence_score', 0):.0%}")

            if contact.get('topics_discussed'):
                print(f"\nTopics Discussed:")
                for topic in contact['topics_discussed'][:5]:
                    print(f"  - {topic}")

            if contact.get('follow_ups'):
                print(f"\nFollow-ups:")
                for followup in contact['follow_ups'][:3]:
                    print(f"  - {followup}")

            # Show raw data if available
            if result.get("raw_data"):
                print(f"\n[DEBUG] Raw transcription:")
                print("-"*70)
                raw_text = result["raw_data"]["full_transcription"]
                print(raw_text[:500] + "..." if len(raw_text) > 500 else raw_text)
                print("-"*70)

        else:
            print(f"\n[ERROR] Status: FAILED")
            print(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_with_audio())
