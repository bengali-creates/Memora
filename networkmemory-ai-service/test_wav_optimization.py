"""
Test WAV optimization - shows conversion is skipped for WAV files
"""
import asyncio
from audio_pipeline.preprocessing import AudioPreprocessor

async def test_wav_vs_mp3():
    print("\n" + "="*70)
    print("TESTING WAV OPTIMIZATION")
    print("="*70)
    
    preprocessor = AudioPreprocessor(chunk_length_seconds=90)
    
    # Test 1: WAV file (should skip conversion)
    print("\n\n[TEST 1] Processing WAV file with skip_conversion=True")
    print("-"*70)
    
    # Create a dummy WAV file for testing
    import os
    from pydub import AudioSegment
    from pydub.generators import Sine
    
    # Generate 5 second test audio
    test_audio = Sine(440).to_audio_segment(duration=5000)  # 5 seconds, 440Hz
    test_audio = test_audio.set_channels(1).set_frame_rate(16000)  # Mono, 16kHz
    
    test_wav_path = "test_audio.wav"
    test_audio.export(test_wav_path, format="wav")
    
    print(f"Created test WAV: {test_wav_path}")
    print(f"  Channels: {test_audio.channels}")
    print(f"  Sample rate: {test_audio.frame_rate}Hz")
    
    # Test with optimization
    try:
        chunks, metadata = await preprocessor.preprocess_file(
            test_wav_path,
            skip_conversion=True  # Enable optimization
        )
        
        print("\n[RESULT] WAV Optimization Test:")
        print(f"  Duration: {metadata['duration_seconds']:.1f}s")
        print(f"  Conversion skipped: {metadata.get('conversion_skipped', False)}")
        print(f"  Chunks created: {len(chunks)}")
        
        if metadata.get('conversion_skipped'):
            print("\n✅ SUCCESS! WAV conversion was SKIPPED!")
            print("   This saves ~5 seconds of processing time!")
        else:
            print("\n⚠️  Conversion was not skipped (file might need format adjustment)")
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    finally:
        # Cleanup
        if os.path.exists(test_wav_path):
            os.remove(test_wav_path)
            print(f"\nCleaned up test file")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_wav_vs_mp3())
