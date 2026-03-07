"""
OpenAI Whisper transcription service (local, free)

Uses the official openai-whisper package
Runs 100% locally on your server - NO API costs!
"""

import whisper
from typing import Dict
from .base import TranscriptionService
from config import settings


class WhisperTranscriptionService(TranscriptionService):
    """
    Local Whisper transcription using openai-whisper package

    Advantages:
    - 100% free (no API costs)
    - Runs locally (privacy)
    - Works offline
    - Good quality

    Disadvantages:
    - Slower than faster-whisper
    - Requires GPU for best speed (works on CPU too)
    """

    def __init__(self):
        """Load Whisper model on initialization"""
        print(f"[LOAD] Loading Whisper model ({settings.WHISPER_MODEL_SIZE})...")
        self.model = whisper.load_model(settings.WHISPER_MODEL_SIZE)
        print("[OK] Whisper model loaded!")

    async def transcribe(self, audio_path: str) -> Dict:
        """
        Transcribe audio using Whisper

        Args:
            audio_path: Path to audio file

        Returns:
            Dict with transcription results
        """
        print(f"[TRANSCRIBE] Transcribing with Whisper ({settings.WHISPER_MODEL_SIZE})...")

        # Transcribe
        result = self.model.transcribe(
            audio_path,
            language=None,  # Auto-detect
            task="transcribe",
            verbose=False
        )

        # Format response
        segments = []
        for segment in result.get("segments", []):
            segments.append({
                "text": segment["text"].strip(),
                "start": segment["start"],
                "end": segment["end"],
                "confidence": segment.get("no_speech_prob", 0.0)
            })
        print(f'transcribes  ${result["text"]}')
        return {
            "text": result["text"],
            "segments": segments,
            "language": result.get("language", "unknown"),
            "duration": segments[-1]["end"] if segments else 0
        }

    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            "name": "OpenAI Whisper",
            "model_size": settings.WHISPER_MODEL_SIZE,
            "type": "local",
            "cost_per_minute": 0.0,  # FREE!
            "privacy": "100% local - audio never leaves your server",
            "speed": "medium (2-3x real-time on CPU, faster on GPU)"
        }
