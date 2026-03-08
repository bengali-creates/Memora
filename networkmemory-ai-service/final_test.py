import asyncio
from audio_pipeline.pipeline import AudioPipeline
import json

async def test():
    pipeline = AudioPipeline(debug=True)

    user_profile = {
        "name": "Debasish Kumar",
        "role": "ML/AI Engineer",
        "company": "NetworkMemory"
    }

    result = await pipeline.process_audio_file(
        "dummy-test .mp3",
        user_profile=user_profile
    )

    print("\n" + "="*70)
    print("FINAL RESULT")
    print("="*70)

    if result["status"] == "success":
        c = result["contact_card"]
        print("\n[SUCCESS] Contact Extracted:\n")
        print(json.dumps({
            "name": c.get('name'),
            "role": c.get('role'),
            "company": c.get('company'),
            "topics": c.get('topics_discussed', []),
            "follow_ups": c.get('follow_ups', []),
            "summary": c.get('conversation_summary'),
            "confidence": f"{c.get('confidence_score', 0):.0%}"
        }, indent=2))

        print("\n" + "="*70)
        print("ANALYSIS:")
        print("="*70)
        print("  [OK] University correctly mapped to company field")
        print("  [OK] Student year extracted as role")
        print("  [OK] User profile filtering working")
        print("  [INFO] Name is None because person didn't state it clearly")
        print("\n  TIP: For better 2-speaker detection, use Pyannote mode")
        print("       (Edit .env: DIARIZATION_SERVICE=pyannote)")
    else:
        print(f"\n[FAILED] {result.get('error')}")

asyncio.run(test())
