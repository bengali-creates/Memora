"""
Transcription services - Factory pattern for easy switching

Usage:
    from services.transcription import get_transcription_service

    transcriber = get_transcription_service()  # Auto-selects based on config
    result = await transcriber.transcribe("audio.wav")
"""

from .base import TranscriptionService
from .whisper_service import WhisperTranscriptionService
from config import settings


def get_transcription_service() -> TranscriptionService:
    """
    Factory function to get the configured transcription service

    Returns the service specified in settings.TRANSCRIPTION_SERVICE

    Supported services:
    - "whisper": OpenAI Whisper (local, free)
    - "faster-whisper": Faster Whisper (local, free, faster) - TODO
    - "assembly": AssemblyAI (API, paid) - TODO

    To switch services, just change TRANSCRIPTION_SERVICE in .env!
    """
    service_name = settings.TRANSCRIPTION_SERVICE.lower()

    if service_name == "whisper":
        return WhisperTranscriptionService()
    # elif service_name == "faster-whisper":
    #     from .faster_whisper_service import FasterWhisperTranscriptionService
    #     return FasterWhisperTranscriptionService()
    # elif service_name == "assembly":
    #     from .assembly_service import AssemblyAITranscriptionService
    #     return AssemblyAITranscriptionService()
    else:
        raise ValueError(
            f"Unknown transcription service: {service_name}. "
            f"Supported: whisper"
        )


__all__ = [
    "TranscriptionService",
    "WhisperTranscriptionService",
    "get_transcription_service"
]
