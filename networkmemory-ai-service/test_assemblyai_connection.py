"""
Test AssemblyAI connection and API key
"""
import asyncio
import os
from dotenv import load_dotenv
import assemblyai as aai

# Load environment
load_dotenv()

def test_api_key():
    """Test 1: Verify API key is loaded"""
    print("\n" + "="*70)
    print("TEST 1: Checking API Key")
    print("="*70)

    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        print("[FAIL] No API key found in environment")
        return False

    print(f"[OK] API key found: {api_key[:8]}...{api_key[-4:]}")
    return True


def test_simple_transcription():
    """Test 2: Try a simple transcription with a very short audio"""
    print("\n" + "="*70)
    print("TEST 2: Simple Transcription Test")
    print("="*70)

    # Create a minimal test audio (1 second of silence)
    import wave
    import numpy as np

    test_file = "test_minimal.wav"
    print(f"[STEP] Creating minimal test audio: {test_file}")

    # Create 1 second of silence at 16kHz
    sample_rate = 16000
    duration = 1  # 1 second
    samples = np.zeros(sample_rate * duration, dtype=np.int16)

    with wave.open(test_file, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())

    print(f"[OK] Created {test_file} ({duration}s, {sample_rate}Hz)")
    print(f"     File size: {os.path.getsize(test_file)} bytes")

    # Set API key
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    aai.settings.api_key = api_key

    print("\n[STEP] Testing AssemblyAI upload...")
    print("       This will test if:")
    print("       - Your internet connection works")
    print("       - Your API key is valid")
    print("       - AssemblyAI service is accessible")
    print("\n       Please wait 10-30 seconds...\n")

    try:
        # Try simple transcription (no diarization)
        config = aai.TranscriptionConfig()
        transcriber = aai.Transcriber()

        print("[1/3] Uploading audio...")
        transcript = transcriber.transcribe(test_file, config)

        print("[2/3] Processing...")
        # The transcribe() call waits for completion

        print("[3/3] Checking result...")

        if transcript.status == aai.TranscriptStatus.error:
            print(f"[FAIL] AssemblyAI returned error: {transcript.error}")
            return False

        print(f"[OK] Transcription successful!")
        print(f"     Status: {transcript.status}")
        print(f"     Text: '{transcript.text}' (expected empty for silence)")
        print(f"     Duration: {transcript.audio_duration}ms")

        # Clean up
        os.remove(test_file)

        return True

    except Exception as e:
        print(f"[FAIL] Exception occurred: {str(e)}")
        print(f"       Error type: {type(e).__name__}")

        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)

        return False


def test_with_actual_audio():
    """Test 3: Try with your actual test audio"""
    print("\n" + "="*70)
    print("TEST 3: Test with Actual Audio File")
    print("="*70)

    test_file = "test_audio_short.wav"

    if not os.path.exists(test_file):
        print(f"[SKIP] Test audio not found: {test_file}")
        print("       Run test_with_small_audio.py first to create it")
        return None

    print(f"[STEP] Testing with: {test_file}")
    file_size = os.path.getsize(test_file) / 1024
    print(f"       File size: {file_size:.2f} KB")

    # Set API key
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    aai.settings.api_key = api_key

    try:
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            speakers_expected=2
        )
        transcriber = aai.Transcriber()

        print("\n[1/3] Uploading...")
        transcript = transcriber.transcribe(test_file, config)

        print("[2/3] Processing...")
        print("[3/3] Checking result...")

        if transcript.status == aai.TranscriptStatus.error:
            print(f"[FAIL] Error: {transcript.error}")
            return False

        print(f"[OK] Success!")
        print(f"     Transcription: {transcript.text[:100]}...")
        print(f"     Speakers: {len(set(u.speaker for u in transcript.utterances))}")

        return True

    except Exception as e:
        print(f"[FAIL] Exception: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ASSEMBLYAI CONNECTION DIAGNOSTIC")
    print("="*70)
    print("\nThis script will test your AssemblyAI connection step by step")
    print("to identify where the timeout is occurring.\n")

    results = []

    # Test 1: API Key
    results.append(("API Key Check", test_api_key()))

    if not results[0][1]:
        print("\n[ABORT] Cannot proceed without API key")
    else:
        # Test 2: Simple transcription
        results.append(("Simple Transcription", test_simple_transcription()))

        # Test 3: Actual audio (only if Test 2 passed)
        if results[1][1]:
            results.append(("Actual Audio", test_with_actual_audio()))

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    for test_name, result in results:
        if result is None:
            status = "[SKIP]"
        elif result:
            status = "[PASS]"
        else:
            status = "[FAIL]"
        print(f"{status} {test_name}")

    print("\n" + "="*70)
    print("DIAGNOSIS")
    print("="*70)

    if not results[0][1]:
        print("ISSUE: API key not found or invalid")
        print("FIX: Check your .env file")
    elif len(results) > 1 and not results[1][1]:
        print("ISSUE: Cannot connect to AssemblyAI")
        print("POSSIBLE CAUSES:")
        print("  1. Internet connection blocked/slow")
        print("  2. Firewall blocking AssemblyAI")
        print("  3. API key invalid or quota exceeded")
        print("  4. AssemblyAI service down")
        print("\nFIX: Try:")
        print("  - Check your internet connection")
        print("  - Try from a different network")
        print("  - Verify API key at https://www.assemblyai.com/app")
        print("  - Check quota usage")
    elif len(results) > 2 and not results[2][1]:
        print("ISSUE: Simple audio works but actual audio fails")
        print("POSSIBLE CAUSES:")
        print("  1. Audio file format issue")
        print("  2. Audio file too large/long")
        print("  3. Audio file corrupted")
    else:
        print("ALL TESTS PASSED!")
        print("Your AssemblyAI connection is working correctly.")
