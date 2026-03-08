"""
Test pipeline with a smaller audio file
"""

import asyncio
import sys
import os
import numpy as np
import soundfile as sf

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_pipeline.pipeline import AudioPipeline


def create_test_audio():
    """Create a short test WAV file with simulated speech"""
    print("[SETUP] Creating test audio file...")

    # Generate 10 seconds of sine wave (simulates speech)
    sample_rate = 16000
    duration = 10  # 10 seconds
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Mix of frequencies to simulate speech
    audio = (
        np.sin(2 * np.pi * 300 * t) +  # 300Hz
        0.5 * np.sin(2 * np.pi * 500 * t) +  # 500Hz
        0.3 * np.sin(2 * np.pi * 800 * t)    # 800Hz
    )

    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.5

    # Save as WAV
    test_audio_path = "test_audio_short.wav"
    sf.write(test_audio_path, audio, sample_rate)

    print(f"[OK] Created test audio: {test_audio_path}")
    print(f"     Duration: {duration}s, Sample rate: {sample_rate}Hz")

    return test_audio_path


async def test_with_small_audio():
    print("\n" + "="*70)
    print("[TEST] TESTING PIPELINE WITH SMALL AUDIO")
    print("="*70)

    # Create test audio
    test_audio_path = create_test_audio()

    # Initialize pipeline
    print("\n[STEP 1] Initializing pipeline...")
    pipeline = AudioPipeline(debug=True)

    print(f"\n[STEP 2] Processing audio...")
    print(f"File: {test_audio_path}")

    try:
        # Process audio from local file (not URL)
        # We'll need to modify this to use process_audio_file instead

        # For now, let's just test the preprocessing
        print("\n[TEST] Testing preprocessing only...")

        chunk_paths, metadata = await pipeline.preprocessor.preprocess_file(
            test_audio_path,
            skip_conversion=True  # It's already WAV
        )

        print(f"\n[OK] Preprocessing successful!")
        print(f"Chunks: {len(chunk_paths)}")
        print(f"Duration: {metadata['duration_seconds']:.1f}s")

        # Now test diarization
        print(f"\n[TEST] Testing diarization with AssemblyAI...")
        print(f"Chunk to process: {chunk_paths[0]}")

        diarization_result = await pipeline.diarizer.diarize(chunk_paths[0])

        print(f"\n[OK] Diarization complete!")
        print(f"Speakers detected: {diarization_result['num_speakers']}")
        print(f"Utterances: {len(diarization_result['utterances'])}")

        # Clean up
        os.remove(test_audio_path)
        for chunk in chunk_paths:
            if os.path.exists(chunk):
                os.remove(chunk)

        print("\n[SUCCESS] Test complete!")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

        # Clean up
        if os.path.exists(test_audio_path):
            os.remove(test_audio_path)


if __name__ == "__main__":
    asyncio.run(test_with_small_audio())
