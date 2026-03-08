"""
Quick test script for your own audio files
"""

import asyncio
import os
from audio_pipeline.pipeline import AudioPipeline

# Your user profile (update with your real info)
MY_PROFILE = {
    "name": "Debasish Kumar",
    "role": "ML/AI Engineer",
    "company": "NetworkMemory",
    "location": "India",
    "bio": "Building AI-powered networking tools",
    "industry": "Technology",
    "experience": "1-3yrs",
    "expertise": ["Machine Learning", "AI Systems", "Python", "FastAPI"],
    "networkingGoals": ["partnerships", "learning", "networking"],
    "interests": ["AI", "Startups", "Hackathons"],
    "followUpStyle": "balanced",
    "conversationStyle": "professional"
}


async def test_audio_file(audio_file: str, profile=None):
    """Test a single audio file"""
    print("\n" + "="*70)
    print(f"TESTING: {audio_file}")
    print("="*70)

    # Check file exists
    if not os.path.exists(audio_file):
        print(f"[ERROR] File not found: {audio_file}")
        return

    # Show file info
    file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
    print(f"\nFile: {audio_file}")
    print(f"Size: {file_size_mb:.2f} MB")
    print(f"Using user profile: {profile.get('name') if profile else 'None'}")
    print()

    # Initialize pipeline
    pipeline = AudioPipeline(debug=True)

    # Optional event context
    event_context = {
        "event_name": "Test Recording",
        "location": "Unknown",
        "timestamp": "2026-03-07"
    }

    # Process audio
    result = await pipeline.process_audio_file(
        audio_file,
        event_context=event_context,
        user_profile=profile
    )

    # Show results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)

    if result["status"] == "success":
        contact = result["contact_card"]

        print("\n[SUCCESS] Contact card extracted!\n")
        print("CONTACT INFORMATION:")
        print("-" * 70)
        print(f"  Name:     {contact.get('name', 'Not mentioned')}")
        print(f"  Role:     {contact.get('role', 'Not mentioned')}")
        print(f"  Company:  {contact.get('company', 'Not mentioned')}")
        print(f"  Email:    {contact.get('email', 'Not mentioned')}")
        print(f"  Phone:    {contact.get('phone', 'Not mentioned')}")
        print(f"  Location: {contact.get('location', 'Not mentioned')}")
        print(f"  LinkedIn: {contact.get('linkedin_url', 'Not mentioned')}")

        topics = contact.get('topics_discussed', [])
        if topics:
            print(f"\n  Topics Discussed:")
            for topic in topics:
                print(f"    • {topic}")

        follow_ups = contact.get('follow_ups', [])
        if follow_ups:
            print(f"\n  Follow-ups:")
            for fu in follow_ups:
                print(f"    • {fu}")

        summary = contact.get('conversation_summary', '')
        if summary:
            print(f"\n  Summary:")
            print(f"    {summary}")

        print(f"\n  Confidence: {contact.get('confidence_score', 0):.0%}")

        print(f"\nMETADATA:")
        print(f"  Processing Time: {result['metadata']['processing_time']:.2f}s")
        print(f"  Audio Duration:  {result['metadata']['audio_duration']:.2f}s")
        print(f"  Speakers:        {result['metadata']['num_speakers']}")

        # Show transcription if available
        if result.get("raw_data"):
            full_text = result['raw_data']['full_transcription']
            print(f"\nFULL TRANSCRIPTION:")
            print("-" * 70)
            if len(full_text) > 500:
                print(f"{full_text[:500]}...")
                print(f"\n[{len(full_text)} characters total]")
            else:
                print(full_text)
            print("-" * 70)

    else:
        print(f"\n[ERROR] Processing failed!")
        print(f"Error: {result.get('error')}")

    print("\n" + "="*70 + "\n")


async def main():
    print("\n")
    print("="*70)
    print(" "*25 + "AUDIO FILE TESTER")
    print("="*70)

    # Find audio files in current directory
    audio_extensions = ('.wav', '.mp3', '.m4a', '.mp4', '.flac', '.ogg')
    audio_files = [
        f for f in os.listdir('.')
        if f.lower().endswith(audio_extensions) and not f.startswith('test_')
    ]

    if not audio_files:
        print("\n[ERROR] No audio files found in current directory!")
        print("\nPlease add your audio files to:")
        print(f"  {os.getcwd()}")
        print(f"\nSupported formats: {', '.join(audio_extensions)}")
        print("\n" + "="*70 + "\n")
        return

    print(f"\nFound {len(audio_files)} audio file(s):")
    for i, f in enumerate(audio_files, 1):
        size_mb = os.path.getsize(f) / (1024 * 1024)
        print(f"  {i}. {f} ({size_mb:.2f} MB)")

    print("\n" + "="*70)

    # Test each file
    for audio_file in audio_files:
        await test_audio_file(audio_file, profile=MY_PROFILE)

    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)
    print("\nCurrent configuration:")
    print("  Mode: Whisper Only (local, no diarization)")
    print("  To switch modes: Edit .env file")
    print("\nTo test again:")
    print("  python test_my_audio.py")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
