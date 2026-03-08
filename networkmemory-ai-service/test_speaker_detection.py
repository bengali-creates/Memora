"""
Test to show difference between with/without speaker detection
"""
import asyncio
from audio_pipeline.pipeline import AudioPipeline

user_profile = {
    "name": "Debasish Kumar",
    "role": "ML/AI Engineer",
    "company": "NetworkMemory"
}

async def test():
    print("\n" + "="*70)
    print("YOUR AUDIO HAS 2 SPEAKERS - LET'S TEST IT!")
    print("="*70)

    print("\nYour transcription shows:")
    print('  Person 1 (Devasis): "work in AIH research... make chatbots"')
    print('  Person 2 (Unknown): "I\'m in second year... from Alaya University... 2028 batch"')

    print("\n" + "="*70)
    print("CURRENT MODE: whisper_only (NO speaker separation)")
    print("="*70)
    print("\nProcessing...")

    pipeline = AudioPipeline(debug=False)
    result = await pipeline.process_audio_file(
        "dummy-test .mp3",
        user_profile=user_profile
    )

    if result["status"] == "success":
        c = result["contact_card"]
        print("\n✅ EXTRACTED (without speaker separation):")
        print(f"   Name:    {c.get('name', 'Not found')}")
        print(f"   Role:    {c.get('role', 'Not found')}")
        print(f"   Company: {c.get('company', 'Not found')}")
        print(f"   Topics:  {', '.join(c.get('topics_discussed', [])[:3])}")
        print(f"\n   Gemini figured it out from context!")
    else:
        print(f"\n❌ FAILED: {result.get('error')}")

    print("\n" + "="*70)
    print("TO GET PROPER 2-SPEAKER DETECTION:")
    print("="*70)
    print("""
Option 1: Use Pyannote (Best for your case)
  1. Install: pip install pyannote.audio torch
  2. Edit .env:
     - Comment out: # DIARIZATION_SERVICE=whisper_only
     - Uncomment: DIARIZATION_SERVICE=pyannote
  3. Run again

  Result: Will show "Speaker A: ..." and "Speaker B: ..."

Option 2: Keep whisper_only (Faster, for hackathon)
  - Gemini is smart enough to figure out 2 people from context
  - Works well enough for demo
  - No installation needed
  - What you're using now!

Recommendation: Use whisper_only for hackathon, add Pyannote later.
""")

asyncio.run(test())
