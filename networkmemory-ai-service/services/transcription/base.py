"""
Base interface for transcription services

This allows easy switching between different transcription models
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class TranscriptionService(ABC):
    """
    Abstract base class for all transcription services

    Any transcription service (Whisper, faster-whisper, AssemblyAI, etc.)
    must implement this interface
    """

    @abstractmethod
    async def transcribe(self, audio_path: str) -> Dict:
        """
        Transcribe audio file to text

        Args:
            audio_path: Path to audio file

        Returns:
            Dict with keys:
                - text: Full transcription
                - segments: List of segments with timestamps
                - language: Detected language
                - duration: Audio duration in seconds
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict:
        """
        Get information about the model being used

        Returns:
            Dict with model name, version, type (local/api), cost info
        """
        pass
