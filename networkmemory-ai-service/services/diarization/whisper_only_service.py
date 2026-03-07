"""
Whisper-only service (no diarization)

This is a simple passthrough service for when you want transcription
but don't need speaker diarization. Useful for:
- Quick testing
- 1-on-1 conversations where you don't need to know who said what
- Demos where Gemini can infer speakers from context

To use proper diarization, switch to 'pyannote' in .env
"""

from typing import Dict, List
from .base import DiarizationService


class WhisperOnlyService(DiarizationService):
    """
    Simple passthrough - no actual diarization

    Just formats transcription as a single speaker conversation.
    Gemini will still extract contact info from context.

    Advantages:
    - Works immediately (no additional setup)
    - No network needed
    - Fast
    - Good enough for demos

    Disadvantages:
    - No speaker separation
    - Can't distinguish user from contact clearly
    """

    def __init__(self):
        """Initialize (no setup needed)"""
        print("[OK] Whisper-only service initialized (no diarization)")
        print("       TIP: For speaker separation, switch to 'pyannote' in .env")

    async def diarize(self, audio_path: str, transcription: str = None) -> Dict:
        """
        Format transcription without diarization

        Args:
            audio_path: Path to audio file (not used)
            transcription: Pre-computed transcription (required)

        Returns:
            Dict with formatted results (no speaker labels)
        """
        if not transcription:
            raise ValueError(
                "WhisperOnlyService requires a transcription. "
                "Make sure TRANSCRIPTION_SERVICE=whisper in .env"
            )

        print("[SPEAKER] Skipping diarization (whisper_only mode)")
        print("   Note: All text will be treated as one conversation")

        # Format as simple conversation without speaker labels
        # Gemini can still extract contact info from context
        utterances = [{
            "speaker": "Speaker",
            "text": transcription,
            "start": 0,
            "end": 0,
            "confidence": 0.8
        }]

        conversation = f"Speaker: {transcription}"

        return {
            "num_speakers": 1,  # Unknown
            "utterances": utterances,
            "conversation": conversation,
            "raw_transcript": transcription
        }

    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            "name": "Whisper Only (No Diarization)",
            "type": "passthrough",
            "cost_per_minute": 0.0,
            "free_tier": "Unlimited",
            "privacy": "100% local",
            "accuracy": "N/A (no diarization)"
        }
