"""
Pyannote.audio diarization service

Uses pyannote.audio for local speaker diarization
100% free and runs entirely on your machine
"""

from typing import Dict, List
from .base import DiarizationService
import torch


class PyannoteDiarizationService(DiarizationService):
    """
    Speaker diarization using pyannote.audio

    Advantages:
    - 100% FREE and local
    - No internet required
    - Privacy-friendly (audio stays on your machine)
    - Good accuracy

    Disadvantages:
    - Slower than API services
    - Requires more compute resources
    - Need to handle transcription separately
    """

    def __init__(self):
        """Initialize pyannote pipeline"""
        from pyannote.audio import Pipeline

        print("[LOAD] Loading pyannote.audio diarization pipeline...")

        # Load pre-trained speaker diarization pipeline
        # This will download the model on first run
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=None  # Public model, no auth needed
        )

        # Use GPU if available for faster processing
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.pipeline.to(device)

        print(f"[OK] Pyannote diarization service initialized (device: {device})")

    async def diarize(self, audio_path: str, transcription: str = None) -> Dict:
        """
        Perform diarization using pyannote.audio

        Args:
            audio_path: Path to audio file
            transcription: Pre-computed transcription (required since pyannote only does diarization)

        Returns:
            Dict with diarization results
        """
        print("[SPEAKER] Diarizing with pyannote.audio...")

        # Run diarization
        diarization = self.pipeline(audio_path)

        # Extract speaker segments
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "speaker": speaker,
                "start": turn.start,
                "end": turn.end
            })

        print(f"   Found {len(segments)} speaker segments")

        # If transcription provided, align it with speaker segments
        if transcription:
            utterances = self._align_transcription_with_segments(
                transcription, segments
            )
        else:
            # Without transcription, just return time segments
            utterances = [
                {
                    "speaker": seg["speaker"],
                    "text": f"[{seg['start']:.1f}s - {seg['end']:.1f}s]",
                    "start": seg["start"],
                    "end": seg["end"],
                    "confidence": 0.85  # pyannote doesn't provide confidence
                }
                for seg in segments
            ]

        # Format conversation
        conversation = self._format_conversation(utterances)

        # Count unique speakers
        speakers = set(utt["speaker"] for utt in utterances)

        return {
            "num_speakers": len(speakers),
            "utterances": utterances,
            "conversation": conversation,
            "raw_transcript": transcription or ""
        }

    def _align_transcription_with_segments(
        self, transcription: str, segments: List[Dict]
    ) -> List[Dict]:
        """
        Align transcription text with speaker segments

        Simple approach: Split transcription by sentences and assign to closest segment
        For better accuracy, you'd want word-level timestamps from transcription
        """
        import re

        # Split transcription into sentences
        sentences = re.split(r'[.!?]+', transcription)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Simple alignment: distribute sentences across segments
        utterances = []
        if len(segments) > 0 and len(sentences) > 0:
            sentences_per_segment = max(1, len(sentences) // len(segments))

            sent_idx = 0
            for seg in segments:
                # Take sentences for this segment
                seg_sentences = sentences[sent_idx:sent_idx + sentences_per_segment]
                if seg_sentences:
                    utterances.append({
                        "speaker": seg["speaker"],
                        "text": ". ".join(seg_sentences) + ".",
                        "start": seg["start"],
                        "end": seg["end"],
                        "confidence": 0.85
                    })
                sent_idx += sentences_per_segment

                # Stop if we've used all sentences
                if sent_idx >= len(sentences):
                    break

            # Add any remaining sentences to last segment
            if sent_idx < len(sentences) and utterances:
                remaining = ". ".join(sentences[sent_idx:]) + "."
                utterances[-1]["text"] += " " + remaining

        return utterances

    def _format_conversation(self, utterances: List[Dict]) -> str:
        """Format utterances into readable conversation"""
        lines = []
        for utt in utterances:
            lines.append(f"{utt['speaker']}: {utt['text']}")
        return "\n".join(lines)

    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            "name": "Pyannote.audio",
            "version": "3.1",
            "type": "local",
            "cost_per_minute": 0.0,  # FREE!
            "free_tier": "Unlimited",
            "privacy": "100% local - audio never leaves your machine",
            "accuracy": "Good"
        }
