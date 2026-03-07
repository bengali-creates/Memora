"""
Modular services for NetworkMemory AI

This package provides pluggable services for transcription, diarization, and extraction.
Switch between different providers by changing config - no code changes needed!

Example:
    # In .env file:
    TRANSCRIPTION_SERVICE=whisper  # or faster-whisper, assembly
    DIARIZATION_SERVICE=assembly   # or pyannote

    # In code - services auto-selected based on config:
    from services.transcription import get_transcription_service
    from services.diarization import get_diarization_service

    transcriber = get_transcription_service()
    diarizer = get_diarization_service()

    result1 = await transcriber.transcribe("audio.wav")
    result2 = await diarizer.diarize("audio.wav")
"""

from .transcription import get_transcription_service, TranscriptionService
from .diarization import get_diarization_service, DiarizationService

__all__ = [
    "get_transcription_service",
    "get_diarization_service",
    "TranscriptionService",
    "DiarizationService"
]
