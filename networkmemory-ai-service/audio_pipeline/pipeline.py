"""
Main Audio Processing Pipeline Orchestrator

This is the conductor - it runs all the modules in sequence:
Audio URL → Preprocess → (Transcribe) → Diarize → Extract → Contact Card

Design pattern: Pipeline/Chain of Responsibility
- Each module does ONE thing
- Modules are independent and testable
- Pipeline combines them in the right order
- Easy to add new steps or modify existing ones
"""

from .preprocessing import AudioPreprocessor
from .extraction import ContactExtractor
from .extraction_ollama import OllamaContactExtractor
from services.diarization import get_diarization_service
from services.transcription import get_transcription_service
from typing import Dict, Optional
import time
from config import settings
from privacy_config import privacy_settings
from privacy_cleanup import PrivacyCleanup, cleanup_after_processing


def get_extractor():
    """
    Factory function to get the configured extraction service

    Returns:
        ContactExtractor or OllamaContactExtractor based on settings
    """
    extraction_service = settings.EXTRACTION_SERVICE.lower()

    if extraction_service == "gemini":
        return ContactExtractor()
    elif extraction_service == "ollama":
        return OllamaContactExtractor(model="llama3")
    else:
        # Default to Gemini
        return ContactExtractor()


class AudioPipeline:
    """
    Complete audio processing pipeline

    Responsibilities:
    1. Coordinate all processing steps
    2. Handle errors gracefully
    3. Track performance metrics
    4. Return structured results

    NOT responsible for:
    - API routing (that's main.py's job)
    - Database storage (that's Node.js's job)
    - Business logic (that's agents' job)
    """

    def __init__(
        self,
        chunk_length: int = None,
        debug: bool = None
    ):
        """
        Initialize pipeline with all components

        Args:
            chunk_length: Audio chunk length in seconds
            debug: Whether to include raw data in responses

        If None, uses values from config.py

        Note: Model selection (transcription, diarization) is now configured
        via .env file - no code changes needed to switch models!
        """
        print("\n" + "="*70)
        print("[*] INITIALIZING AUDIO PROCESSING PIPELINE")
        print("="*70)

        # Use config defaults if not specified
        if chunk_length is None:
            chunk_length = settings.CHUNK_LENGTH_SECONDS
        if debug is None:
            debug = settings.DEBUG

        self.debug = debug

        # Initialize all components
        print("\n[1/4] Initializing Audio Preprocessor...")
        self.preprocessor = AudioPreprocessor(chunk_length_seconds=chunk_length)

        print("\n[2/4] Initializing Transcription Service...")
        print(f"   Using: {settings.TRANSCRIPTION_SERVICE}")
        self.transcriber = get_transcription_service()

        print("\n[3/4] Initializing Diarization Service...")
        print(f"   Using: {settings.DIARIZATION_SERVICE}")
        self.diarizer = get_diarization_service()

        print("\n[4/4] Initializing Contact Extractor...")
        print(f"   Using: {settings.EXTRACTION_SERVICE}")
        self.extractor = get_extractor()

        print("\n" + "="*70)
        print("[OK] PIPELINE READY")
        print("="*70 + "\n")

    async def process_audio(
        self,
        audio_url: str,
        event_context: Optional[Dict[str, str]] = None,
        user_profile: Optional[Dict] = None
    ) -> Dict:
        """
        Process audio file end-to-end

        Flow:
        1. Download & preprocess audio
        2. Transcribe (speech to text)
        3. Diarize speakers (identify who spoke when)
        4. Extract contact information (with user profile filtering)
        5. Return structured results

        Args:
            audio_url: URL to audio file
            event_context: Optional dict with event info
            user_profile: Optional dict with user's profile info
                         Used to filter out user's own information

        Returns:
            Dict with:
            - status: "success" or "error"
            - contact_card: Extracted contact info (if success)
            - metadata: Processing metrics
            - raw_data: Intermediate results (if debug mode)
            - error: Error message (if failed)

        Why this order:
        1. Preprocessing first: Need clean audio
        2. Transcription: Convert speech to text (can skip if using all-in-one service)
        3. Diarization: Identify speakers (can use transcription or do both together)
        4. Extraction last: Needs conversation + user profile to filter correctly
        """
        print("\n" + "="*70)
        print("[AUDIO] AUDIO PROCESSING PIPELINE STARTED")
        print("="*70)
        print(f"Audio URL: {audio_url}")
        if event_context:
            print(f"Event: {event_context.get('event_name', 'Unknown')}")

        pipeline_start = time.time()

        # Track files for cleanup
        downloaded_path = None
        chunk_paths = []

        try:
            # ============================================
            # STEP 1: Preprocessing
            # ============================================
            print("\n" + "-"*70)
            print("[STEP 1/3] AUDIO PREPROCESSING")
            print("-"*70)

            chunk_paths, prep_metadata = await self.preprocessor.preprocess(audio_url)

            # Note: We don't have direct access to intermediate files here
            # but preprocessing creates temp files that should be cleaned up

            # For simplicity, process first chunk only
            # In production, you might process all chunks and merge results
            # For networking conversations (usually < 5 min), one chunk is enough
            if not chunk_paths:
                raise Exception("Preprocessing produced no audio chunks")

            main_audio_path = chunk_paths[0]
            print(f"\nUsing audio chunk: {main_audio_path}")

            # ============================================
            # STEP 2: Transcription & Diarization
            # ============================================
            # Check if diarization service does transcription too (like AssemblyAI)
            diarization_service = settings.DIARIZATION_SERVICE.lower()

            if diarization_service == "assembly":
                # AssemblyAI does both transcription + diarization in one call
                print("\n" + "-"*70)
                print("[STEP 2/4] TRANSCRIPTION + DIARIZATION (Combined)")
                print("-"*70)
                print("   Service: AssemblyAI (all-in-one)")

                diarization_result = await self.diarizer.diarize(main_audio_path)

            else:
                # Separate transcription and diarization (e.g., Whisper + Pyannote)
                print("\n" + "-"*70)
                print("[STEP 2/4] TRANSCRIPTION")
                print("-"*70)

                transcription_result = await self.transcriber.transcribe(main_audio_path)
                full_transcript = transcription_result["text"]

                print(f"\n[DEBUG] Transcription complete:")
                print(f"   Length: {len(full_transcript)} characters")
                print(f"   Language: {transcription_result.get('language', 'unknown')}")
                print(f"   Preview: {full_transcript[:200]}...")

                print("\n" + "-"*70)
                print("[STEP 3/4] SPEAKER DIARIZATION")
                print("-"*70)

                # Pass transcription to diarization service
                diarization_result = await self.diarizer.diarize(
                    main_audio_path,
                    transcription=full_transcript
                )

            # Quality check: Make sure we got a conversation
            if diarization_result["num_speakers"] < 2:
                print("\n[WARNING] Only 1 speaker detected. This might not be a conversation.")
                # Continue anyway, but flag low confidence

            # ============================================
            # STEP 4: Contact Extraction
            # ============================================
            print("\n" + "-"*70)
            print("[STEP 4/4] CONTACT INFORMATION EXTRACTION")
            print("-"*70)

            if user_profile:
                print(f"   Using user profile: {user_profile.get('name', 'Unknown')}")

            contact_card = self.extractor.extract_contact(
                diarization_result["conversation"],
                event_context,
                user_profile=user_profile
            )

            # ============================================
            # STEP 5: Package Results
            # ============================================
            print("\n" + "-"*70)
            print("[STEP 5/5] PACKAGING RESULTS")
            print("-"*70)

            pipeline_elapsed = time.time() - pipeline_start

            # Build metadata
            metadata = {
                "audio_duration": prep_metadata["duration_seconds"],
                "num_speakers": diarization_result["num_speakers"],
                "processing_time": pipeline_elapsed,
                "utterances_count": len(diarization_result["utterances"])
            }

            # Build result
            result = {
                "status": "success",
                "contact_card": contact_card,
                "metadata": metadata
            }

            # Add raw data if debug mode AND privacy settings allow
            if self.debug and privacy_settings.STORE_DEBUG_DATA:
                result["raw_data"] = {
                    "full_transcription": diarization_result["raw_transcript"],
                    "diarized_conversation": diarization_result["conversation"],
                    "utterances": diarization_result["utterances"]
                }
            elif self.debug and not privacy_settings.STORE_DEBUG_DATA:
                if privacy_settings.LOG_PROCESSING_ACTIVITIES:
                    print(f"[PRIVACY] Debug data not included (STORE_DEBUG_DATA=false)")

            # ============================================
            # PRIVACY: Cleanup temporary files
            # ============================================
            if privacy_settings.DELETE_AUDIO_AFTER_PROCESSING:
                print("\n[PRIVACY] Cleaning up temporary audio files...")
                cleanup_after_processing(chunk_paths=chunk_paths)

            # ============================================
            # PRIVACY: Sanitize response
            # ============================================
            result = PrivacyCleanup.sanitize_response_data(result)

            # ============================================
            # Success Summary
            # ============================================
            print("\n" + "="*70)
            print("[OK] PIPELINE COMPLETE - SUCCESS")
            print("="*70)
            print(f"[TIME]  Processing time: {pipeline_elapsed:.2f}s")
            print(f" Contact: {contact_card.get('name', 'Unknown')}")
            print(f" Company: {contact_card.get('company', 'Unknown')}")
            print(f" Role: {contact_card.get('role', 'Unknown')}")
            print(f" Confidence: {contact_card.get('confidence_score', 0):.0%}")
            print(f"  Speakers: {diarization_result['num_speakers']}")
            print(f" Utterances: {len(diarization_result['utterances'])}")

            # Show topics if any
            topics = contact_card.get('topics_discussed', [])
            if topics:
                print(f"[INFO] Topics: {', '.join(topics[:5])}")

            # Show follow-ups if any
            followups = contact_card.get('follow_ups', [])
            if followups:
                print(f"[OK] Follow-ups: {', '.join(followups[:3])}")

            print("="*70 + "\n")

            return result

        except Exception as e:
            # ============================================
            # Error Handling
            # ============================================
            pipeline_elapsed = time.time() - pipeline_start

            # PRIVACY: Cleanup even on error
            if privacy_settings.DELETE_AUDIO_AFTER_PROCESSING and chunk_paths:
                print("\n[PRIVACY] Cleaning up temporary audio files (error recovery)...")
                cleanup_after_processing(chunk_paths=chunk_paths)

            print("\n" + "="*70)
            print("[ERROR] PIPELINE FAILED")
            print("="*70)
            print(f"Error: {str(e)}")
            print(f"[TIME]  Failed after: {pipeline_elapsed:.2f}s")
            print("="*70 + "\n")

            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "processing_time": pipeline_elapsed
                }
            }

    async def process_audio_file(
        self,
        audio_file_path: str,
        event_context: Optional[Dict[str, str]] = None,
        user_profile: Optional[Dict] = None
    ) -> Dict:
        """
        Process a local audio file (convenience method)

        Args:
            audio_file_path: Path to local audio file
            event_context: Optional event info
            user_profile: Optional user profile for filtering

        Returns:
            Same as process_audio()

        This is a convenience wrapper around process_audio() for local files.
        The preprocessing module handles local files the same way as URLs.
        """
        import os

        if not os.path.exists(audio_file_path):
            return {
                "status": "error",
                "error": f"Audio file not found: {audio_file_path}",
                "metadata": {"processing_time": 0}
            }

        # Convert to file:// URL format that preprocessing expects
        # Actually, preprocessing.preprocess() can handle local paths directly
        return await self.process_audio(
            audio_file_path,
            event_context=event_context,
            user_profile=user_profile
        )

    def get_pipeline_info(self) -> Dict:
        """
        Get information about the pipeline configuration

        Useful for debugging and monitoring
        """
        return {
            "diarization_service": settings.DIARIZATION_SERVICE,
            "transcription_service": settings.TRANSCRIPTION_SERVICE,
            "extraction_service": settings.EXTRACTION_SERVICE,
            "chunk_length": self.preprocessor.chunk_length_seconds,
            "debug_mode": self.debug,
            "diarization_info": self.diarizer.get_model_info()
        }


# ============================================
# Test Function
# ============================================

async def test_pipeline():
    """
    Test complete pipeline with sample audio

    To run: python -m audio_pipeline.pipeline
    """
    print("\n🧪 TESTING COMPLETE PIPELINE\n")

    # Initialize pipeline
    pipeline = AudioPipeline(debug=True)

    # Print pipeline info
    info = pipeline.get_pipeline_info()
    print("\n📋 Pipeline Configuration:")
    for key, value in info.items():
        print(f"  {key}: {value}")

    # Test with sample audio
    test_audio_url = "https://storage.googleapis.com/aai-docs-samples/espn.m4a"

    event_context = {
        "event_name": "DevFest Kolkata 2026",
        "location": "Kolkata, India",
        "timestamp": "2026-03-04T15:30:00Z"
    }

    print(f"\n🎯 Processing test audio...")
    print(f"URL: {test_audio_url}")

    result = await pipeline.process_audio(test_audio_url, event_context)

    if result["status"] == "success":
        print("\n" + "="*70)
        print("[OK] PIPELINE TEST SUCCESSFUL!")
        print("="*70)

        print(f"\n📇 Contact Card:")
        import json
        print(json.dumps(result["contact_card"], indent=2))

        print(f"\n Metadata:")
        print(json.dumps(result["metadata"], indent=2))

        if result.get("raw_data"):
            print(f"\n Conversation Preview:")
            conv_text = result["raw_data"]["diarized_conversation"]
            preview_lines = conv_text.split('\n')[:5]
            for line in preview_lines:
                print(f"  {line}")
            if len(conv_text.split('\n')) > 5:
                print(f"  ... ({len(conv_text.split(' '))-5} more lines)")

    else:
        print("\n" + "="*70)
        print("[ERROR] PIPELINE TEST FAILED")
        print("="*70)
        print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_pipeline())
