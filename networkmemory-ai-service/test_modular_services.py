"""
Test script for modular services

This demonstrates how easy it is to use and switch between services
"""

import asyncio
from services import get_transcription_service, get_diarization_service
from config import settings, print_settings


async def test_services():
    """Test the modular service architecture"""

    print("\n" + "="*70)
    print("🧪 TESTING MODULAR SERVICES")
    print("="*70 + "\n")

    # Print current configuration
    print_settings()

    # Initialize services based on config
    print("\n" + "="*70)
    print("📦 INITIALIZING SERVICES")
    print("="*70 + "\n")

    try:
        transcriber = get_transcription_service()
        print(f"✅ Transcription service loaded: {transcriber.__class__.__name__}")
        print(f"   Info: {transcriber.get_model_info()}\n")
    except Exception as e:
        print(f"❌ Failed to load transcription service: {e}\n")
        transcriber = None

    try:
        diarizer = get_diarization_service()
        print(f"✅ Diarization service loaded: {diarizer.__class__.__name__}")
        print(f"   Info: {diarizer.get_model_info()}\n")
    except Exception as e:
        print(f"❌ Failed to load diarization service: {e}\n")
        diarizer = None

    # Show how to switch services
    print("\n" + "="*70)
    print("🔄 HOW TO SWITCH SERVICES")
    print("="*70 + "\n")

    print("Just edit your .env file and change:")
    print("")
    print("# For Transcription:")
    print('TRANSCRIPTION_SERVICE=whisper          # Current (local, free)')
    print('# TRANSCRIPTION_SERVICE=faster-whisper  # Faster (local, free) - TODO')
    print('# TRANSCRIPTION_SERVICE=assembly        # API-based - TODO')
    print("")
    print("# For Diarization:")
    print('DIARIZATION_SERVICE=assembly           # Current (API, accurate)')
    print('# DIARIZATION_SERVICE=pyannote          # Local, free - TODO')
    print("")
    print("Then restart the server - that's it! NO code changes needed.")

    print("\n" + "="*70)
    print("✅ MODULAR ARCHITECTURE TEST COMPLETE!")
    print("="*70 + "\n")

    return transcriber, diarizer


if __name__ == "__main__":
    asyncio.run(test_services())
