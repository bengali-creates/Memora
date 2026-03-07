"""
Speech-to-Text Transcription Module

Uses faster-whisper for efficient local transcription

Why faster-whisper over OpenAI Whisper API:
1. FREE - no API costs
2. FASTER - 4x faster than original Whisper
3. PRIVATE - audio never leaves your server
4. OFFLINE - works without internet (after initial model download)

Model size trade-offs:
- tiny: Fastest but lowest accuracy (~50% WER)
- base: Good balance - RECOMMENDED FOR HACKATHON
- small: Better accuracy, 2x slower
- medium: High accuracy, 4x slower
- large: Best accuracy, 8x slower (overkill for networking convos)
"""

from faster_whisper import WhisperModel
from typing import List, Dict, Optional
import time
from config import settings


class Transcriber:
    """
    Handles speech-to-text transcription using Whisper

    Design decisions:
    - Load model once (on init) - don't reload for each file
    - Use VAD filter - removes silence, improves accuracy
    - Return structured segments - useful for timeline building later
    """

    def __init__(
        self,
        model_size: str = None,
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        """
        Initialize Whisper model

        Args:
            model_size: Model size (tiny, base, small, medium, large-v2)
                       If None, uses config.WHISPER_MODEL_SIZE
            device: "cpu" or "cuda" (GPU)
            compute_type: "int8" (faster, less accurate) or "float16" (slower, more accurate)

        Why int8:
        - 4x faster than float16
        - Minimal accuracy loss for speech
        - Works on CPU (no GPU needed)
        """
        if model_size is None:
            model_size = settings.WHISPER_MODEL_SIZE

        print(f"\n🔵 Loading Whisper model...")
        print(f"   Model: {model_size}")
        print(f"   Device: {device}")
        print(f"   Compute type: {compute_type}")

        start_time = time.time()

        # Load model (first time downloads ~140MB for base model)
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )

        load_time = time.time() - start_time

        print(f"[OK] Whisper model loaded in {load_time:.2f}s")

        self.model_size = model_size

    def transcribe_chunk(
        self,
        audio_path: str,
        language: Optional[str] = "en"
    ) -> Dict:
        """
        Transcribe a single audio chunk

        Args:
            audio_path: Path to audio file
            language: Language code (e.g., "en", "hi", "es")
                     Set to None for auto-detection (slower but works for any language)

        Returns:
            Dict with:
            - text: Full transcription
            - language: Detected/specified language
            - duration: Audio duration
            - segments: List of segments with timestamps
            - processing_time: Time taken to transcribe

        Why segment-level data:
        - Useful for showing "what was said when"
        - Can highlight specific parts in UI
        - Helps with speaker attribution
        """
        print(f"\n🎤 Transcribing: {audio_path}")
        start_time = time.time()

        try:
            # Transcribe with optimal settings
            segments, info = self.model.transcribe(
                audio_path,
                language=language,  # Specify language for speed, None for auto-detect
                beam_size=5,  # Beam search size (higher = more accurate but slower)
                                # 5 is good balance
                vad_filter=True,  # Voice Activity Detection - removes silence
                vad_parameters=dict(
                    min_silence_duration_ms=500  # Treat 500ms+ silence as pause
                                                  # Helps segment sentences naturally
                )
            )

            # Collect segments
            transcription_segments = []
            full_text_parts = []

            for segment in segments:
                seg_dict = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                }
                transcription_segments.append(seg_dict)
                full_text_parts.append(segment.text.strip())

            full_transcription = " ".join(full_text_parts)
            processing_time = time.time() - start_time

            print(f"[OK] Transcription complete in {processing_time:.2f}s")
            print(f"   Language: {info.language}")
            print(f"   Duration: {info.duration:.1f}s")
            print(f"   Segments: {len(transcription_segments)}")
            print(f"   Preview: {full_transcription[:100]}...")

            return {
                "text": full_transcription,
                "language": info.language,
                "duration": info.duration,
                "segments": transcription_segments,
                "processing_time": processing_time,
                "num_segments": len(transcription_segments)
            }

        except Exception as e:
            print(f"[ERROR] Transcription failed: {str(e)}")
            raise

    def transcribe_chunks(self, chunk_paths: List[str]) -> Dict:
        """
        Transcribe multiple audio chunks and combine results

        Why combine:
        - Long conversations might be split into chunks
        - Need to present as single continuous transcription
        - But keep individual chunk metadata for debugging

        Args:
            chunk_paths: List of paths to audio chunk files

        Returns:
            Combined transcription with metadata
        """
        print("\n" + "="*70)
        print("🎤 TRANSCRIPTION PIPELINE")
        print("="*70)

        all_transcriptions = []
        all_segments = []
        total_duration = 0
        total_processing_time = 0

        for i, chunk_path in enumerate(chunk_paths):
            print(f"\n[PACKAGE] Processing chunk {i+1}/{len(chunk_paths)}")

            result = self.transcribe_chunk(chunk_path)

            all_transcriptions.append(result["text"])
            # Adjust segment timestamps for chunks after the first one
            offset = total_duration
            for seg in result["segments"]:
                all_segments.append({
                    "start": seg["start"] + offset,
                    "end": seg["end"] + offset,
                    "text": seg["text"]
                })

            total_duration += result["duration"]
            total_processing_time += result["processing_time"]

        # Combine all transcriptions
        combined_text = " ".join(all_transcriptions)

        print("\n" + "="*70)
        print("[OK] TRANSCRIPTION COMPLETE")
        print(f"   Total duration: {total_duration:.1f}s")
        print(f"   Total segments: {len(all_segments)}")
        print(f"   Processing time: {total_processing_time:.2f}s")
        print(f"   Text length: {len(combined_text)} characters")
        print("="*70 + "\n")

        return {
            "text": combined_text,
            "segments": all_segments,
            "duration": total_duration,
            "num_chunks": len(chunk_paths),
            "processing_time": total_processing_time
        }


# ============================================
# Test Function
# ============================================

def test_transcription():
    """
    Test transcription with a sample audio file

    To run: python -m audio_pipeline.transcription
    """
    print("\n🧪 Testing Transcription\n")

    transcriber = Transcriber(model_size="base")

    # You need a test audio file
    # Either run preprocessing first, or use a local audio file
    test_audio = "/tmp/audio_converted.wav"

    import os
    if not os.path.exists(test_audio):
        print(f"[ERROR] Test audio not found: {test_audio}")
        print("   Run preprocessing first to generate test audio")
        print("   Or provide a path to a local WAV file")
        return

    try:
        result = transcriber.transcribe_chunk(test_audio)

        print("\n[OK] Test Successful!")
        print(f"\nTranscription:")
        print(f"  {result['text']}")
        print(f"\nMetadata:")
        print(f"  Language: {result['language']}")
        print(f"  Duration: {result['duration']:.1f}s")
        print(f"  Segments: {result['num_segments']}")
        print(f"  Processing time: {result['processing_time']:.2f}s")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")


if __name__ == "__main__":
    test_transcription()
