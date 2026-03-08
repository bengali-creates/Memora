"""
Test to verify file path issue is fixed
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_pipeline.preprocessing import AudioPreprocessor


async def test_path_fix():
    print("\n[TEST] Testing File Path Fix\n")
    print("="*70)

    # Initialize preprocessor
    preprocessor = AudioPreprocessor(chunk_length_seconds=90)

    # Test with AssemblyAI's sample audio (m4a format)
    test_audio_url = "https://storage.googleapis.com/aai-docs-samples/espn.m4a"

    print(f"\nTest URL: {test_audio_url}")
    print("Expected: File should be saved as '.m4a', not '.tmp'")
    print("="*70)

    try:
        # Test download only
        print("\n[TEST 1] Testing download with proper extension...")
        downloaded_path = await preprocessor.download_audio(test_audio_url)

        print(f"\n[RESULT] Downloaded file path: {downloaded_path}")
        print(f"         Extension: {os.path.splitext(downloaded_path)[1]}")
        print(f"         File exists: {os.path.exists(downloaded_path)}")

        if not downloaded_path.endswith('.tmp'):
            print("[OK] SUCCESS: File extension preserved correctly!")
        else:
            print("[FAIL] FAIL: Still using .tmp extension")
            return

        # Test conversion
        print("\n[TEST 2] Testing conversion with proper path...")
        wav_path = preprocessor.convert_to_wav(downloaded_path)

        print(f"\n[RESULT] Converted file path: {wav_path}")
        print(f"         File exists: {os.path.exists(wav_path)}")

        if os.path.exists(wav_path):
            print("[OK] SUCCESS: Conversion worked with proper file path!")
        else:
            print("[FAIL] FAIL: Conversion failed")
            return

        print("\n" + "="*70)
        print("[SUCCESS] ALL TESTS PASSED - File path issue is FIXED!")
        print("="*70)

        # Clean up
        if os.path.exists(downloaded_path):
            os.remove(downloaded_path)
        if os.path.exists(wav_path) and wav_path != downloaded_path:
            os.remove(wav_path)

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_path_fix())
