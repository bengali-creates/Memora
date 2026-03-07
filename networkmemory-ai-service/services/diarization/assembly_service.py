"""
AssemblyAI diarization service

Uses AssemblyAI API for speaker diarization
Provides excellent accuracy for speaker separation
"""

import assemblyai as aai
from typing import Dict, List
from .base import DiarizationService
from config import settings


class AssemblyAIDiarizationService(DiarizationService):
    """
    Speaker diarization using AssemblyAI

    Advantages:
    - Excellent accuracy
    - Handles transcription + diarization in one call
    - Robust to noisy audio

    Disadvantages:
    - API call (requires internet)
    - 5 hours/month free tier
    - Audio sent to external server
    """

    def __init__(self):
        """Initialize AssemblyAI client"""
        aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
        print("[OK] AssemblyAI diarization service initialized")

    async def diarize(self, audio_path: str, transcription: str = None) -> Dict:
        """
        Perform diarization using AssemblyAI

        Args:
            audio_path: Path to audio file
            transcription: Not used (AssemblyAI does its own transcription)

        Returns:
            Dict with diarization results
        """
        print("[SPEAKER] Diarizing with AssemblyAI...")
        print(f"   Audio file: {audio_path}")

        import os
        if os.path.exists(audio_path):
            file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
            print(f"   File size: {file_size_mb:.2f} MB")
        else:
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Configure transcription with diarization
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            speakers_expected=2,  # Assume 2 speakers for networking conversations
            # Add language detection
            language_detection=True
        )

        # Transcribe with diarization
        print("   [1/3] Uploading audio to AssemblyAI...")
        transcriber = aai.Transcriber()

        try:
            # Submit transcription job
            transcript = transcriber.transcribe(audio_path, config)
            print("   [2/3] Audio uploaded successfully!")
            print("   [3/3] Transcribing and diarizing (this may take 30-60 seconds)...")

            # The transcript object handles polling automatically
            # But we can check status

        except Exception as e:
            print(f"   [ERROR] Failed during upload/transcription: {str(e)}")
            raise Exception(f"AssemblyAI connection error: {str(e)}")

        # Check completion status
        if transcript.status == aai.TranscriptStatus.error:
            print(f"   [ERROR] Transcription failed: {transcript.error}")
            raise Exception(f"AssemblyAI error: {transcript.error}")

        print("   [OK] Transcription completed!")

        # DEBUG: Show transcription
        print("\n" + "="*70)
        print("[DEBUG] TRANSCRIPTION RESULT")
        print("="*70)
        print(f"Status: {transcript.status}")
        print(f"Full text length: {len(transcript.text)} characters")
        print(f"\nFull transcription:")
        print("-"*70)
        print(transcript.text)
        print("-"*70)

        # Extract utterances
        utterances = []
        for utterance in transcript.utterances:
            utterances.append({
                "speaker": utterance.speaker,
                "text": utterance.text,
                "start": utterance.start / 1000.0,  # Convert ms to seconds
                "end": utterance.end / 1000.0,
                "confidence": utterance.confidence
            })

        # DEBUG: Show utterances
        print(f"\n[DEBUG] Found {len(utterances)} utterances")
        print("First 3 utterances:")
        for i, utt in enumerate(utterances[:3]):
            print(f"  {i+1}. {utt['speaker']}: {utt['text'][:100]}...")

        # Format conversation
        conversation = self._format_conversation(utterances)

        # Count unique speakers
        speakers = set(utt["speaker"] for utt in utterances)
        print(f"\n[DEBUG] Detected {len(speakers)} speakers: {', '.join(speakers)}")
        print("="*70 + "\n")

        return {
            "num_speakers": len(speakers),
            "utterances": utterances,
            "conversation": conversation,
            "raw_transcript": transcript.text
        }

    def _format_conversation(self, utterances: List[Dict]) -> str:
        """Format utterances into readable conversation"""
        lines = []
        for utt in utterances:
            lines.append(f"{utt['speaker']}: {utt['text']}")
        return "\n".join(lines)

    def identify_user_vs_contact(
        self,
        utterances: List[Dict],
        user_name: str = None
    ) -> Dict[str, str]:
        """
        Try to identify which speaker is the user vs the contact

        Strategy:
        1. If user_name provided, search for it in utterances
        2. First person to introduce themselves = usually the user
        3. Fallback: Speaker A = user, Speaker B = contact

        Args:
            utterances: List of utterance dicts
            user_name: Optional name of the user

        Returns:
            Dict mapping speaker labels:
            {"Speaker A": "user", "Speaker B": "contact"}

        Why this matters:
        - We want to extract the CONTACT's info, not the user's
        - "I work at Google" - need to know who said it!
        """
        speaker_mapping = {}

        # Strategy 1: Search for user name
        if user_name:
            user_name_lower = user_name.lower()
            for utt in utterances[:5]:  # Check first 5 utterances (intro phase)
                if user_name_lower in utt['text'].lower():
                    speaker_mapping[utt['speaker']] = "user"
                    break

        # Strategy 2: First introduction
        intro_keywords = ["i'm", "my name", "this is"]
        for utt in utterances[:5]:
            text_lower = utt['text'].lower()
            if any(keyword in text_lower for keyword in intro_keywords):
                if utt['speaker'] not in speaker_mapping:
                    speaker_mapping[utt['speaker']] = "user"
                    break

        # Map remaining speakers
        all_speakers = list(set(u['speaker'] for u in utterances))
        for speaker in all_speakers:
            if speaker not in speaker_mapping:
                speaker_mapping[speaker] = "contact" if len(speaker_mapping) == 0 else "other"

        return speaker_mapping

    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            "name": "AssemblyAI",
            "type": "api",
            "cost_per_minute": 0.00625,  # $0.37/hour
            "free_tier": "5 hours/month",
            "privacy": "Audio sent to AssemblyAI servers",
            "accuracy": "Excellent"
        }
