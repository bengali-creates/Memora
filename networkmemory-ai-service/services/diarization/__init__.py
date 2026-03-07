"""
Diarization services - Factory pattern for easy switching

Usage:
    from services.diarization import get_diarization_service

    diarizer = get_diarization_service()  # Auto-selects based on config
    result = await diarizer.diarize("audio.wav")
"""

from .base import DiarizationService
from .assembly_service import AssemblyAIDiarizationService
from config import settings


def get_diarization_service() -> DiarizationService:
    """
    Factory function to get the configured diarization service

    Returns the service specified in settings.DIARIZATION_SERVICE

    Supported services:
    - "assembly": AssemblyAI (API, accurate, 5hrs free/month, does transcription + diarization)
    - "pyannote": Pyannote.audio (local, free, diarization only)
    - "whisper_only": No diarization (good for quick testing)

    To switch services, just change DIARIZATION_SERVICE in .env!
    """
    service_name = settings.DIARIZATION_SERVICE.lower()

    if service_name == "assembly":
        return AssemblyAIDiarizationService()
    elif service_name == "pyannote":
        from .pyannote_service import PyannoteDiarizationService
        return PyannoteDiarizationService()
    elif service_name == "whisper_only":
        from .whisper_only_service import WhisperOnlyService
        return WhisperOnlyService()
    else:
        raise ValueError(
            f"Unknown diarization service: {service_name}. "
            f"Supported: assembly, pyannote, whisper_only"
        )


__all__ = [
    "DiarizationService",
    "AssemblyAIDiarizationService",
    "get_diarization_service"
]
