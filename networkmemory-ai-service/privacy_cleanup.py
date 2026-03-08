"""
Privacy-focused Cleanup Utilities

Handles automatic deletion of temporary files, audio, and transcripts
according to privacy settings.

DPDP Compliance: Data Minimization & Storage Limitation
"""

import os
import time
from typing import List
from privacy_config import privacy_settings


class PrivacyCleanup:
    """
    Handles cleanup of sensitive data according to privacy settings

    Key Features:
    - Automatic deletion of temp files
    - Logging for compliance audit
    - Safe deletion (catches errors, doesn't fail pipeline)
    """

    @staticmethod
    def delete_file(file_path: str, file_type: str = "file") -> bool:
        """
        Safely delete a file

        Args:
            file_path: Path to file to delete
            file_type: Type of file for logging (e.g., "audio", "transcript")

        Returns:
            True if deleted, False if failed
        """
        if not os.path.exists(file_path):
            return False

        try:
            # Get file size before deletion (for logging)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            # Delete file
            os.remove(file_path)

            if privacy_settings.LOG_PROCESSING_ACTIVITIES:
                print(f"[PRIVACY] Deleted {file_type}: {os.path.basename(file_path)} ({file_size_mb:.2f} MB)")

            return True

        except Exception as e:
            print(f"[WARNING] Failed to delete {file_type} {os.path.basename(file_path)}: {e}")
            return False

    @staticmethod
    def delete_files(file_paths: List[str], file_type: str = "file") -> int:
        """
        Delete multiple files

        Args:
            file_paths: List of file paths to delete
            file_type: Type of files for logging

        Returns:
            Number of files successfully deleted
        """
        if not file_paths:
            return 0

        deleted_count = 0
        for file_path in file_paths:
            if PrivacyCleanup.delete_file(file_path, file_type):
                deleted_count += 1

        if privacy_settings.LOG_PROCESSING_ACTIVITIES and deleted_count > 0:
            print(f"[PRIVACY] Deleted {deleted_count}/{len(file_paths)} {file_type}(s)")

        return deleted_count

    @staticmethod
    def cleanup_audio_files(chunk_paths: List[str], original_path: str = None) -> None:
        """
        Delete audio files according to privacy settings

        Args:
            chunk_paths: List of audio chunk file paths
            original_path: Original audio file path (if different from chunks)
        """
        if not privacy_settings.DELETE_AUDIO_AFTER_PROCESSING:
            return

        # Delete chunks
        PrivacyCleanup.delete_files(chunk_paths, "audio chunk")

        # Delete original if specified
        if original_path and original_path not in chunk_paths:
            PrivacyCleanup.delete_file(original_path, "original audio")

    @staticmethod
    def cleanup_intermediate_files(
        downloaded_path: str = None,
        converted_path: str = None,
        cleaned_path: str = None
    ) -> None:
        """
        Delete intermediate processing files

        Args:
            downloaded_path: Downloaded audio file
            converted_path: Converted WAV file
            cleaned_path: Noise-reduced file
        """
        if not privacy_settings.DELETE_AUDIO_AFTER_PROCESSING:
            return

        intermediate_files = [
            (downloaded_path, "downloaded audio"),
            (converted_path, "converted audio"),
            (cleaned_path, "cleaned audio")
        ]

        for file_path, file_type in intermediate_files:
            if file_path and os.path.exists(file_path):
                PrivacyCleanup.delete_file(file_path, file_type)

    @staticmethod
    def sanitize_contact_card(contact_card: dict) -> dict:
        """
        Remove sensitive data from contact card according to privacy settings

        Args:
            contact_card: Contact card dict

        Returns:
            Sanitized contact card
        """
        # Make a copy to avoid modifying original
        sanitized = contact_card.copy()

        # Remove raw conversation if privacy settings say so
        if not privacy_settings.STORE_RAW_CONVERSATION:
            if "raw_conversation" in sanitized:
                if privacy_settings.LOG_PROCESSING_ACTIVITIES:
                    conv_length = len(sanitized["raw_conversation"])
                    print(f"[PRIVACY] Removed raw_conversation ({conv_length} chars) from contact card")
                del sanitized["raw_conversation"]

        return sanitized

    @staticmethod
    def sanitize_response_data(result: dict) -> dict:
        """
        Remove sensitive debug data from API response

        Args:
            result: API response dict

        Returns:
            Sanitized response
        """
        # Make a copy
        sanitized = result.copy()

        # Remove debug data in production
        if not privacy_settings.STORE_DEBUG_DATA:
            if "raw_data" in sanitized:
                if privacy_settings.LOG_PROCESSING_ACTIVITIES:
                    print(f"[PRIVACY] Removed raw_data from API response")
                del sanitized["raw_data"]

        # Sanitize contact card
        if "contact_card" in sanitized:
            sanitized["contact_card"] = PrivacyCleanup.sanitize_contact_card(sanitized["contact_card"])

        return sanitized


class CleanupContext:
    """
    Context manager for automatic cleanup

    Usage:
        async with CleanupContext() as cleanup:
            chunks, metadata = await preprocess(audio_url)
            cleanup.register_for_cleanup(chunks, "audio chunks")
            # ... do processing ...
            # Cleanup happens automatically when exiting context
    """

    def __init__(self):
        self.files_to_cleanup: List[tuple[str, str]] = []  # List of (path, type)
        self.file_lists_to_cleanup: List[tuple[List[str], str]] = []  # List of (paths, type)

    def register_for_cleanup(self, file_path: str, file_type: str = "file"):
        """Register a file for cleanup"""
        self.files_to_cleanup.append((file_path, file_type))

    def register_list_for_cleanup(self, file_paths: List[str], file_type: str = "file"):
        """Register multiple files for cleanup"""
        self.file_lists_to_cleanup.append((file_paths, file_type))

    async def __aenter__(self):
        """Enter async context"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context - perform cleanup"""
        if not privacy_settings.DELETE_AUDIO_AFTER_PROCESSING:
            return

        # Cleanup individual files
        for file_path, file_type in self.files_to_cleanup:
            PrivacyCleanup.delete_file(file_path, file_type)

        # Cleanup file lists
        for file_paths, file_type in self.file_lists_to_cleanup:
            PrivacyCleanup.delete_files(file_paths, file_type)


# Convenience functions
def cleanup_after_processing(
    chunk_paths: List[str] = None,
    downloaded_path: str = None,
    converted_path: str = None,
    cleaned_path: str = None
) -> None:
    """
    Clean up all temporary files after processing

    Args:
        chunk_paths: Audio chunk files
        downloaded_path: Downloaded audio
        converted_path: Converted audio
        cleaned_path: Cleaned audio
    """
    if chunk_paths:
        PrivacyCleanup.cleanup_audio_files(chunk_paths)

    PrivacyCleanup.cleanup_intermediate_files(
        downloaded_path=downloaded_path,
        converted_path=converted_path,
        cleaned_path=cleaned_path
    )


if __name__ == "__main__":
    # Test cleanup utilities
    from privacy_config import print_privacy_settings

    print_privacy_settings()

    print("\n" + "="*70)
    print("CLEANUP UTILITIES LOADED")
    print("="*70)
    print(f"✅ Audio cleanup: {'Enabled' if privacy_settings.DELETE_AUDIO_AFTER_PROCESSING else 'Disabled'}")
    print(f"✅ Transcript cleanup: {'Enabled' if privacy_settings.DELETE_TRANSCRIPTS_AFTER_EXTRACTION else 'Disabled'}")
    print("="*70)
