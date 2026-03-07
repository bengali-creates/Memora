"""
Base interface for speaker diarization services

This allows easy switching between different diarization models
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class DiarizationService(ABC):
    """
    Abstract base class for all diarization services

    Any diarization service (AssemblyAI, Pyannote, etc.)
    must implement this interface
    """

    @abstractmethod
    async def diarize(self, audio_path: str, transcription: str = None) -> Dict:
        """
        Perform speaker diarization on audio

        Args:
            audio_path: Path to audio file
            transcription: Optional pre-computed transcription (to avoid re-transcribing)

        Returns:
            Dict with keys:
                - num_speakers: Number of speakers detected
                - utterances: List of utterances with speaker labels
                - conversation: Formatted conversation string
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

    def identify_user_vs_contact(
        self,
        utterances: List[Dict],
        user_name: str = None
    ) -> Dict[str, str]:
        """
        Identify which speaker is the user vs the contact

        Optional method - provides default implementation
        Subclasses can override for better logic

        Args:
            utterances: List of utterance dicts
            user_name: Optional name of the user

        Returns:
            Dict mapping speaker labels to roles
        """
        # Default implementation - can be overridden
        speaker_mapping = {}
        all_speakers = list(set(u['speaker'] for u in utterances))

        for i, speaker in enumerate(all_speakers):
            speaker_mapping[speaker] = "user" if i == 0 else "contact"

        return speaker_mapping
