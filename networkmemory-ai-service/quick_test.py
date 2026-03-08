import asyncio
from audio_pipeline.pipeline import AudioPipeline

async def test():
    pipeline = AudioPipeline(debug=False)  # Less output

    user_profile = {
        "name": "Debasish Kumar",
        "role": "ML/AI Engineer",
        "company": "NetworkMemory",
        "location": "India"
    }

    result = await pipeline.process_audio_file(
        "dummy-test .mp3",
        user_profile=user_profile
    )

    if result["status"] == "success":
        c = result["contact_card"]
        print("\n✅ SUCCESS!\n")
        print(f"Name:    {c.get('name')}")
        print(f"Role:    {c.get('role')}")
        print(f"Company: {c.get('company')}")
        print(f"Topics:  {', '.join(c.get('topics_discussed', []))}")
        print(f"\nSummary: {c.get('conversation_summary')}")
        print(f"\nConfidence: {c.get('confidence_score', 0):.0%}")
    else:
        print(f"\n❌ FAILED: {result.get('error')}")

asyncio.run(test())
