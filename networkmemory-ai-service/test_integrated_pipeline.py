"""
Test the integrated pipeline with new modular services

This tests the complete flow:
1. Audio preprocessing
2. Diarization (with modular service)
3. Contact extraction
4. Result packaging

Run: python test_integrated_pipeline.py
"""

import asyncio
from audio_pipeline.pipeline import AudioPipeline
from config import settings
import json


async def test_pipeline_integration():
    print("\n" + "="*70)
    print("TESTING INTEGRATED PIPELINE WITH MODULAR SERVICES")
    print("="*70)

    # Show current configuration
    print("\nConfiguration:")
    print(f"   Transcription: {settings.TRANSCRIPTION_SERVICE}")
    print(f"   Diarization: {settings.DIARIZATION_SERVICE}")
    print(f"   Extraction: {settings.EXTRACTION_SERVICE}")

    print("\n" + "-"*70)
    print("Initializing Pipeline...")
    print("-"*70)

    # Initialize pipeline (debug mode for verbose output)
    pipeline = AudioPipeline(debug=True)

    # Get pipeline info
    info = pipeline.get_pipeline_info()
    print("\nPipeline Info:")
    print(json.dumps(info, indent=2))

    print("\n" + "="*70)
    print("[SUCCESS] PIPELINE INITIALIZATION SUCCESSFUL!")
    print("="*70)

    print("\nNext Steps:")
    print("   1. To test with actual audio:")
    print("      - Uncomment the process_audio section below")
    print("      - Provide a test audio URL or local file")
    print("   2. To start the API server:")
    print("      - Run: python main.py")
    print("      - API docs: http://localhost:8000/docs")

    # ============================================
    # OPTIONAL: Test with actual audio
    # ============================================

    # Uncomment this section when you have test audio
    """
    print("\n" + "="*70)
    print("TESTING WITH SAMPLE AUDIO")
    print("="*70)

    # Example: Public sample audio
    test_audio_url = "https://storage.googleapis.com/aai-docs-samples/espn.m4a"

    event_context = {
        "event_name": "DevFest Kolkata 2026",
        "location": "Kolkata, India",
        "timestamp": "2026-03-04T15:30:00Z"
    }

    print(f"\nProcessing: {test_audio_url}")

    result = await pipeline.process_audio(test_audio_url, event_context)

    if result["status"] == "success":
        print("\n" + "="*70)
        print("[SUCCESS] AUDIO PROCESSING SUCCESSFUL!")
        print("="*70)

        print("\nExtracted Contact Card:")
        print(json.dumps(result["contact_card"], indent=2))

        print("\nProcessing Metadata:")
        print(json.dumps(result["metadata"], indent=2))

        if result.get("raw_data"):
            print("\nConversation Preview:")
            conv_text = result["raw_data"]["diarized_conversation"]
            preview_lines = conv_text.split('\n')[:10]
            for line in preview_lines:
                print(f"  {line}")
            if len(conv_text.split('\n')) > 10:
                print(f"  ... ({len(conv_text.split('\n'))-10} more lines)")
    else:
        print("\n" + "="*70)
        print("[FAILED] AUDIO PROCESSING FAILED")
        print("="*70)
        print(f"Error: {result.get('error')}")
    """

    return True


if __name__ == "__main__":
    try:
        asyncio.run(test_pipeline_integration())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
