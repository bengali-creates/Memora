"""
Test all external API connections

Run this FIRST before building anything else!

This verifies:
1. All API keys are correct
2. All services are accessible
3. Basic functionality works

To run:
    python tests/test_apis.py

Or with pytest:
    pytest tests/test_apis.py -v
"""

import os
import sys

# Add parent directory to path so we can import from root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
import google.generativeai as genai
import assemblyai as aai
from elevenlabs import generate, set_api_key
from openai import OpenAI

load_dotenv()


def test_gemini_api():
    """Test Gemini API connection"""
    print("\n" + "="*70)
    print("🔵 Testing Gemini API")
    print("="*70)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        response = model.generate_content("Say 'Hello from Gemini!' and nothing else.")
        print(f"✅ Response: {response.text}")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_assemblyai_api():
    """Test AssemblyAI API connection"""
    print("\n" + "="*70)
    print("🔵 Testing AssemblyAI API")
    print("="*70)

    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        print("❌ ASSEMBLYAI_API_KEY not found in environment")
        return False

    try:
        aai.settings.api_key = api_key

        # Test with AssemblyAI's sample audio
        transcriber = aai.Transcriber()
        audio_url = "https://storage.googleapis.com/aai-docs-samples/espn.m4a"

        print(f"   Transcribing sample audio (this takes ~30 seconds)...")
        config = aai.TranscriptionConfig(speaker_labels=False)
        transcript = transcriber.transcribe(audio_url, config)

        if transcript.status == aai.TranscriptStatus.error:
            print(f"❌ Transcription failed: {transcript.error}")
            return False

        print(f"✅ Transcription successful!")
        print(f"   Text preview: {transcript.text[:100]}...")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_elevenlabs_api():
    """Test ElevenLabs API connection"""
    print("\n" + "="*70)
    print("🔵 Testing ElevenLabs API")
    print("="*70)

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found in environment")
        return False

    try:
        set_api_key(api_key)

        print("   Generating test audio...")
        audio = generate(
            text="Hello from ElevenLabs!",
            voice="Rachel",
            model="eleven_monolingual_v1"
        )

        print(f"✅ Generated {len(audio)} bytes of audio")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_openai_embeddings():
    """Test OpenAI Embeddings API"""
    print("\n" + "="*70)
    print("🔵 Testing OpenAI Embeddings API")
    print("="*70)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False

    try:
        client = OpenAI(api_key=api_key)

        print("   Creating test embedding...")
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="This is a test embedding for NetworkMemory AI"
        )

        embedding = response.data[0].embedding
        print(f"✅ Embedding created successfully")
        print(f"   Dimension: {len(embedding)}")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all API tests"""
    print("\n" + "="*70)
    print("🧪 TESTING ALL API CONNECTIONS")
    print("="*70)
    print("\nThis will verify that all your API keys are working correctly.")
    print("Make sure you've set up your .env file first!\n")

    results = {
        "Gemini": test_gemini_api(),
        "AssemblyAI": test_assemblyai_api(),
        "ElevenLabs": test_elevenlabs_api(),
        "OpenAI Embeddings": test_openai_embeddings()
    }

    # Print summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)

    all_passed = True
    for api_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {api_name}")
        if not passed:
            all_passed = False

    print("="*70)

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("You're ready to build the pipeline.\n")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Fix the errors above before continuing.")
        print("Check your .env file and API keys.\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
