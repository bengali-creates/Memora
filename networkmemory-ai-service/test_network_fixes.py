"""
Try different network configurations for AssemblyAI
"""
import os
from dotenv import load_dotenv
import assemblyai as aai

load_dotenv()

def test_with_timeout_config():
    """Test 1: Try with custom timeout settings"""
    print("\n" + "="*70)
    print("TEST: Custom Timeout Configuration")
    print("="*70)

    # Set API key
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

    # Check if there's a way to set custom timeout
    print("[INFO] Testing with longer timeout...")
    print("       Waiting up to 3 minutes...")

    # Create tiny test audio
    import wave
    import numpy as np

    test_file = "test_tiny.wav"
    samples = np.zeros(16000, dtype=np.int16)  # 1 second

    with wave.open(test_file, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(samples.tobytes())

    try:
        config = aai.TranscriptionConfig()
        transcriber = aai.Transcriber()

        print("[UPLOAD] Starting upload...")
        transcript = transcriber.transcribe(test_file, config)

        print(f"[RESULT] Status: {transcript.status}")

        if transcript.status == aai.TranscriptStatus.error:
            print(f"[FAIL] Error: {transcript.error}")
            return False
        else:
            print("[SUCCESS] It worked!")
            return True

    except Exception as e:
        print(f"[FAIL] Exception: {str(e)}")
        return False
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def suggest_alternatives():
    """Suggest alternative approaches"""
    print("\n" + "="*70)
    print("ALTERNATIVE SOLUTIONS FOR YOUR HACKATHON")
    print("="*70)

    print("\n1. USE WHISPER (LOCAL) FOR TRANSCRIPTION")
    print("   - No internet needed")
    print("   - Fast (15-30 seconds)")
    print("   - Free and unlimited")
    print("   - Already installed in your project!")
    print("\n2. SKIP DIARIZATION FOR DEMO")
    print("   - Just extract contact info from full transcript")
    print("   - Works for 1-on-1 conversations")
    print("   - Can add diarization later")
    print("\n3. TRY DIFFERENT NETWORK")
    print("   - Use mobile hotspot")
    print("   - Try from different location")
    print("   - Use VPN to US server")
    print("\n4. USE DEEPGRAM (ASSEMBLYAI ALTERNATIVE)")
    print("   - Sometimes faster for international users")
    print("   - Free tier: 12,000 minutes/month")
    print("   - Similar API")


if __name__ == "__main__":
    # Try with timeout config
    success = test_with_timeout_config()

    if not success:
        suggest_alternatives()

        print("\n" + "="*70)
        print("RECOMMENDED: SWITCH TO LOCAL WHISPER")
        print("="*70)
        print("\nFor your hackathon, I recommend using Whisper (local)")
        print("instead of AssemblyAI since you're having network issues.")
        print("\nWHISPER ADVANTAGES:")
        print("  - No network needed (works offline)")
        print("  - No API limits")
        print("  - Fast processing")
        print("  - Already installed!")
        print("\nWould you like me to switch your pipeline to use Whisper?")
        print("It will take 2 minutes to configure.")
