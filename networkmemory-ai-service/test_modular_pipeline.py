"""
Test the modular pipeline with user profile support

This demonstrates:
1. Whisper transcription (local, no network)
2. Optional diarization (can add Pyannote later)
3. User profile filtering (Gemini extracts only CONTACT info)
"""

import asyncio
from audio_pipeline.pipeline import AudioPipeline

# Sample user profile (matching your TypeScript types)
sample_user_profile = {
    # Identity
    "name": "Debasish Kumar",
    "role": "ML/AI Engineer",
    "company": "NetworkMemory",
    "location": "India",
    "bio": "Building AI-powered networking tools",

    # Professional
    "industry": "Technology",
    "experience": "1-3yrs",
    "expertise": ["Machine Learning", "AI Systems", "Python", "FastAPI"],

    # Networking
    "networkingGoals": ["partnerships", "learning", "networking"],

    # Interests
    "interests": ["AI", "Startups", "Hackathons"],

    # Preferences
    "followUpStyle": "balanced",
    "conversationStyle": "professional"
}


async def test_with_local_file():
    """Test with a local audio file"""
    print("\n" + "="*70)
    print("TEST: Modular Pipeline with User Profile")
    print("="*70)
    print("\nCurrent Configuration:")
    print("  - Transcription: Whisper (local)")
    print("  - Diarization: whisper_only (no speaker separation)")
    print("  - Extraction: Gemini with user profile filtering")
    print("\nTo switch to Pyannote diarization later:")
    print("  1. Install: pip install pyannote.audio")
    print("  2. Update .env: DIARIZATION_SERVICE=pyannote")
    print("  3. Run again!")
    print("\n" + "="*70 + "\n")

    # Initialize pipeline
    pipeline = AudioPipeline(debug=True)

    # Check if test audio exists
    import os
    test_audio = "test_audio_short.wav"

    if not os.path.exists(test_audio):
        print(f"[INFO] Creating test audio: {test_audio}")
        # Create simple test audio
        import wave
        import numpy as np

        sample_rate = 16000
        duration = 10  # 10 seconds
        samples = np.zeros(sample_rate * duration, dtype=np.int16)

        with wave.open(test_audio, 'w') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(samples.tobytes())

        print(f"[OK] Created {test_audio}")
        print("[NOTE] This is silent audio for testing. Use your own recording for real test!\n")

    # Event context
    event_context = {
        "event_name": "DevFest Kolkata 2026",
        "location": "Kolkata, India",
        "timestamp": "2026-03-07T10:00:00Z"
    }

    print(f"[TEST] Processing audio with user profile...")
    print(f"       User: {sample_user_profile['name']}")
    print(f"       Audio: {test_audio}\n")

    # Process with user profile
    result = await pipeline.process_audio_file(
        test_audio,
        event_context=event_context,
        user_profile=sample_user_profile
    )

    # Display results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)

    if result["status"] == "success":
        contact = result["contact_card"]

        print(f"\n[OK] Pipeline completed successfully!\n")
        print(f"Contact Card:")
        print(f"  Name: {contact.get('name', 'Not mentioned')}")
        print(f"  Role: {contact.get('role', 'Not mentioned')}")
        print(f"  Company: {contact.get('company', 'Not mentioned')}")
        print(f"  Email: {contact.get('email', 'Not mentioned')}")
        print(f"  Phone: {contact.get('phone', 'Not mentioned')}")
        print(f"  Location: {contact.get('location', 'Not mentioned')}")

        topics = contact.get('topics_discussed', [])
        if topics:
            print(f"\n  Topics Discussed:")
            for topic in topics:
                print(f"    - {topic}")

        follow_ups = contact.get('follow_ups', [])
        if follow_ups:
            print(f"\n  Follow-ups:")
            for fu in follow_ups:
                print(f"    - {fu}")

        summary = contact.get('conversation_summary', '')
        if summary:
            print(f"\n  Summary:")
            print(f"    {summary}")

        print(f"\n  Confidence: {contact.get('confidence_score', 0):.0%}")

        print(f"\n Metadata:")
        print(f"  Processing Time: {result['metadata']['processing_time']:.2f}s")
        print(f"  Audio Duration: {result['metadata']['audio_duration']:.2f}s")
        print(f"  Speakers Detected: {result['metadata']['num_speakers']}")

        # Show raw transcription if debug mode
        if result.get("raw_data"):
            print(f"\n[DEBUG] Full Transcription:")
            print(f"  {result['raw_data']['full_transcription'][:200]}...")

    else:
        print(f"\n[ERROR] Pipeline failed!")
        print(f"  Error: {result.get('error')}")

    print("\n" + "="*70)
    print("NEXT STEPS FOR YOUR HACKATHON")
    print("="*70)
    print("""
1. RECORD A REAL CONVERSATION:
   - Use your phone to record a 30-60 second networking conversation
   - Save as .wav, .mp3, or .m4a
   - Replace test_audio_short.wav with your recording

2. TEST THE PIPELINE:
   - Run this script again with your audio
   - Verify that Gemini correctly identifies the CONTACT (not you)
   - Check that your information is filtered out

3. ADD DIARIZATION (Optional, after hackathon):
   - Install: pip install pyannote.audio
   - Update .env: DIARIZATION_SERVICE=pyannote
   - Run again to get speaker labels

4. INTEGRATE WITH FRONTEND:
   - Your React Native app uploads audio to /api/audio/process-upload
   - Include user_profile in the request
   - Receive contact card in response

5. DATABASE INTEGRATION:
   - Fetch user profile from your Node.js backend
   - Pass it to the Python service
   - Gemini will filter out user info automatically
""")
    print("="*70 + "\n")


async def test_with_real_conversation():
    """Test with a real recorded conversation"""
    print("\n" + "="*70)
    print("TEST: Real Conversation")
    print("="*70)

    # Check if user has uploaded their own audio
    import os
    audio_files = [f for f in os.listdir('.') if f.endswith(('.wav', '.mp3', '.m4a'))]
    audio_files = [f for f in audio_files if not f.startswith('test_')]

    if not audio_files:
        print("\n[INFO] No real audio files found!")
        print("       Please record a conversation and save it in this directory.")
        print("       Supported formats: .wav, .mp3, .m4a\n")
        return

    print(f"\n[INFO] Found audio files:")
    for i, f in enumerate(audio_files, 1):
        file_size = os.path.getsize(f) / (1024 * 1024)
        print(f"  {i}. {f} ({file_size:.2f} MB)")

    print(f"\n[TEST] Using: {audio_files[0]}\n")

    # Initialize pipeline
    pipeline = AudioPipeline(debug=True)

    # Process
    result = await pipeline.process_audio_file(
        audio_files[0],
        user_profile=sample_user_profile
    )

    # Show results
    if result["status"] == "success":
        print(f"\n[OK] Successfully extracted contact!")
        print(f"     Name: {result['contact_card'].get('name', 'Unknown')}")
        print(f"     Company: {result['contact_card'].get('company', 'Unknown')}")
    else:
        print(f"\n[ERROR] Failed: {result.get('error')}")


if __name__ == "__main__":
    print("\n")
    print("=" * 70)
    print(" " * 20 + "MODULAR PIPELINE TEST")
    print("=" * 70)

    # Run test
    asyncio.run(test_with_local_file())

    # Uncomment to test with real audio:
    # asyncio.run(test_with_real_conversation())
