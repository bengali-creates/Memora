"""
Speaker Diarization Module

"Who said what?" - Separates speakers in a conversation

Why diarization is critical:
- Need to know which person is the USER vs the CONTACT
- "I work at Google" - who said this? Changes everything!
- Helps identify follow-ups and action items
- Better conversation summary

Why AssemblyAI:
1. Best free tier diarization (5 hours/month)
2. More accurate than open-source alternatives
3. Simple API, good docs
4. Also does transcription (but we use Whisper locally for cost)
"""

import os
import assemblyai as aai
from typing import Dict, List
import time
from config import settings


class Diarizer:
    """
    Handles speaker diarization using AssemblyAI

    Design pattern:
    - Upload audio → AssemblyAI processes → Get results
    - Results include: who spoke when, what they said
    - Format as "Speaker A: text" for easy Gemini extraction
    """

    def __init__(self):
        """
        Initialize AssemblyAI

        API key from environment variables (config.py)
        """
        api_key = settings.ASSEMBLYAI_API_KEY

        if not api_key:
            raise ValueError(
                "ASSEMBLYAI_API_KEY not found in environment variables. "
                "Get one from https://www.assemblyai.com/"
            )

        aai.settings.api_key = api_key
        print("[OK] AssemblyAI initialized")

    def diarize_audio(
        self,
        audio_path: str,
        speakers_expected: int = 2
    ) -> Dict:
        """
        Perform speaker diarization on audio file

        Args:
            audio_path: Path to audio file (any format)
            speakers_expected: Expected number of speakers
                              2 = typical networking conversation
                              3+ = group conversations (less common)

        Returns:
            Dict with:
            - full_text: Complete transcription
            - utterances: List of who said what when
            - conversation_text: Formatted conversation
            - num_speakers: Actual speakers detected
            - processing_time: Time taken

        Why utterances:
        - Each utterance = one person speaking continuously
        - Includes timing, speaker label, confidence
        - More granular than just "Speaker A said X, Speaker B said Y"
        """
        print(f"\n[SPEAKER] Diarizing audio: {audio_path}")
        print(f"   Expected speakers: {speakers_expected}")
        start_time = time.time()

        try:
            # Configure transcription with speaker labels
            config = aai.TranscriptionConfig(
                speaker_labels=True,  # Enable diarization
                speakers_expected=speakers_expected  # Hint for better accuracy
                                                     # (AssemblyAI can still detect more/less)
            )

            # Create transcriber and transcribe
            transcriber = aai.Transcriber()
            print("   ⏳ Uploading and processing (this may take 30-60 seconds)...")

            transcript = transcriber.transcribe(audio_path, config)

            # Check for errors
            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(f"Diarization failed: {transcript.error}")

            processing_time = time.time() - start_time

            # Process utterances
            utterances = []
            for utterance in transcript.utterances:
                utterances.append({
                    "speaker": f"Speaker {utterance.speaker}",  # "Speaker A", "Speaker B", etc.
                    "text": utterance.text,
                    "start": utterance.start / 1000,  # Convert ms to seconds
                    "end": utterance.end / 1000,
                    "confidence": utterance.confidence
                })

            # Format as conversation text
            # This format makes it easy for Gemini to understand the conversation
            conversation_text = "\n".join([
                f"{u['speaker']}: {u['text']}"
                for u in utterances
            ])

            # Count unique speakers
            unique_speakers = len(set(u['speaker'] for u in utterances))

            print(f"[OK] Diarization complete in {processing_time:.2f}s")
            print(f"   Speakers detected: {unique_speakers}")
            print(f"   Utterances: {len(utterances)}")
            print(f"\n Conversation preview:")
            # Show first 3 utterances
            preview_lines = conversation_text.split('\n')[:3]
            for line in preview_lines:
                print(f"   {line}")
            if len(utterances) > 3:
                print(f"   ... ({len(utterances) - 3} more utterances)")

            return {
                "full_text": transcript.text,  # Complete transcription without speaker labels
                "utterances": utterances,  # Detailed utterance-by-utterance data
                "conversation_text": conversation_text,  # Formatted conversation
                "num_speakers": unique_speakers,  # Actual speakers found
                "processing_time": processing_time
            }

        except Exception as e:
            print(f"[ERROR] Diarization failed: {str(e)}")
            raise

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


# ============================================
# Test Function
# ============================================

def test_diarization():
    """
    Test diarization with a sample audio file

    To run: python -m audio_pipeline.diarization
    """
    print("\n🧪 Testing Speaker Diarization\n")

    diarizer = Diarizer()

    # Test audio - needs to be a real conversation
    test_audio = "/tmp/audio_converted.wav"

    import os
    if not os.path.exists(test_audio):
        print(f"[ERROR] Test audio not found: {test_audio}")
        print("   Run preprocessing first to generate test audio")
        return

    try:
        result = diarizer.diarize_audio(test_audio)

        print("\n[OK] Test Successful!")
        print(f"\nFull Conversation:")
        print(result['conversation_text'])

        print(f"\nMetadata:")
        print(f"  Speakers: {result['num_speakers']}")
        print(f"  Utterances: {len(result['utterances'])}")
        print(f"  Processing time: {result['processing_time']:.2f}s")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")


if __name__ == "__main__":
    test_diarization()
