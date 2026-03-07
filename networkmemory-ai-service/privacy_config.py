"""
Privacy Configuration for NetworkMemory AI Service

This module defines privacy settings and data retention policies
to comply with DPDP (Digital Personal Data Protection) Act 2023 in India.

Key Principles:
1. Data Minimization - Collect and retain only what's necessary
2. Storage Limitation - Delete data as soon as it's no longer needed
3. User Rights - Allow users to access, correct, and delete their data
4. Transparency - Clear notice about what is collected and why
"""

import os
from dotenv import load_dotenv

load_dotenv()


class PrivacySettings:
    """
    Privacy and data retention configuration

    All settings can be configured via environment variables
    """

    # ============================================
    # Data Retention Settings
    # ============================================

    # Delete audio files immediately after processing (RECOMMENDED)
    DELETE_AUDIO_AFTER_PROCESSING: bool = os.getenv("DELETE_AUDIO_AFTER_PROCESSING", "true").lower() == "true"

    # Delete full transcripts after extraction (RECOMMENDED)
    DELETE_TRANSCRIPTS_AFTER_EXTRACTION: bool = os.getenv("DELETE_TRANSCRIPTS_AFTER_EXTRACTION", "true").lower() == "true"

    # Store raw conversation text in contact card (NOT RECOMMENDED for privacy)
    # If False, only summary is stored
    STORE_RAW_CONVERSATION: bool = os.getenv("STORE_RAW_CONVERSATION", "false").lower() == "true"

    # Store full diarized conversation in debug mode (NOT RECOMMENDED for production)
    STORE_DEBUG_DATA: bool = os.getenv("STORE_DEBUG_DATA", "false").lower() == "true"

    # ============================================
    # Data Processing Settings
    # ============================================

    # Use local models instead of external APIs where possible
    USE_LOCAL_MODELS: bool = os.getenv("USE_LOCAL_MODELS", "false").lower() == "true"

    # Anonymize speaker names in transcripts (replace with "Speaker A", "Speaker B")
    ANONYMIZE_SPEAKERS: bool = os.getenv("ANONYMIZE_SPEAKERS", "false").lower() == "true"

    # ============================================
    # External API Settings
    # ============================================

    # For Gemini API - ensure no data is used for training
    # Note: Gemini's free tier already doesn't train on your data
    # But you should verify this in Google's terms
    GEMINI_NO_TRAINING: bool = True  # Always true for Gemini

    # ============================================
    # User Rights Settings
    # ============================================

    # Allow users to request their data
    ENABLE_DATA_ACCESS_REQUEST: bool = True

    # Allow users to delete their data
    ENABLE_DATA_DELETION_REQUEST: bool = True

    # Allow users to correct their data
    ENABLE_DATA_CORRECTION_REQUEST: bool = True

    # ============================================
    # Audit & Logging
    # ============================================

    # Log data processing activities (for compliance)
    LOG_PROCESSING_ACTIVITIES: bool = os.getenv("LOG_PROCESSING_ACTIVITIES", "true").lower() == "true"

    # Log data deletion requests (for compliance)
    LOG_DELETION_REQUESTS: bool = os.getenv("LOG_DELETION_REQUESTS", "true").lower() == "true"

    # ============================================
    # Consent Management
    # ============================================

    # Require explicit consent before recording
    REQUIRE_CONSENT: bool = os.getenv("REQUIRE_CONSENT", "true").lower() == "true"

    # Require consent from all parties in conversation (stricter)
    REQUIRE_ALL_PARTY_CONSENT: bool = os.getenv("REQUIRE_ALL_PARTY_CONSENT", "false").lower() == "true"

    # ============================================
    # Helper Methods
    # ============================================

    @classmethod
    def get_privacy_summary(cls) -> dict:
        """
        Get a summary of current privacy settings

        Returns:
            Dict with privacy configuration
        """
        return {
            "data_minimization": {
                "delete_audio_after_processing": cls.DELETE_AUDIO_AFTER_PROCESSING,
                "delete_transcripts_after_extraction": cls.DELETE_TRANSCRIPTS_AFTER_EXTRACTION,
                "store_raw_conversation": cls.STORE_RAW_CONVERSATION,
                "store_debug_data": cls.STORE_DEBUG_DATA
            },
            "processing": {
                "use_local_models": cls.USE_LOCAL_MODELS,
                "anonymize_speakers": cls.ANONYMIZE_SPEAKERS
            },
            "user_rights": {
                "data_access": cls.ENABLE_DATA_ACCESS_REQUEST,
                "data_deletion": cls.ENABLE_DATA_DELETION_REQUEST,
                "data_correction": cls.ENABLE_DATA_CORRECTION_REQUEST
            },
            "consent": {
                "require_consent": cls.REQUIRE_CONSENT,
                "require_all_party_consent": cls.REQUIRE_ALL_PARTY_CONSENT
            }
        }

    @classmethod
    def validate_for_production(cls) -> tuple[bool, list[str]]:
        """
        Validate that privacy settings are appropriate for production

        Returns:
            Tuple of (is_valid, list of warnings)
        """
        warnings = []

        # Check critical privacy settings
        if cls.STORE_RAW_CONVERSATION:
            warnings.append("⚠️ STORE_RAW_CONVERSATION is enabled - full conversations will be stored")

        if cls.STORE_DEBUG_DATA:
            warnings.append("⚠️ STORE_DEBUG_DATA is enabled - sensitive debug data will be stored")

        if not cls.DELETE_AUDIO_AFTER_PROCESSING:
            warnings.append("⚠️ DELETE_AUDIO_AFTER_PROCESSING is disabled - audio files will be retained")

        if not cls.DELETE_TRANSCRIPTS_AFTER_EXTRACTION:
            warnings.append("⚠️ DELETE_TRANSCRIPTS_AFTER_EXTRACTION is disabled - transcripts will be retained")

        if not cls.REQUIRE_CONSENT:
            warnings.append("⚠️ REQUIRE_CONSENT is disabled - may not be DPDP compliant")

        is_valid = len(warnings) == 0
        return is_valid, warnings

    @classmethod
    def get_recommended_production_config(cls) -> str:
        """
        Get recommended .env configuration for production

        Returns:
            String with recommended environment variables
        """
        return """
# ============================================
# RECOMMENDED PRIVACY SETTINGS FOR PRODUCTION
# ============================================

# Data Minimization - Delete Everything After Processing
DELETE_AUDIO_AFTER_PROCESSING=true
DELETE_TRANSCRIPTS_AFTER_EXTRACTION=true
STORE_RAW_CONVERSATION=false
STORE_DEBUG_DATA=false

# Privacy Protection
USE_LOCAL_MODELS=false  # Set to true if you have local models
ANONYMIZE_SPEAKERS=false  # Not needed if data is deleted

# Compliance
LOG_PROCESSING_ACTIVITIES=true
LOG_DELETION_REQUESTS=true

# Consent (REQUIRED for DPDP compliance)
REQUIRE_CONSENT=true
REQUIRE_ALL_PARTY_CONSENT=false  # Set to true for maximum privacy
"""


# Create global settings instance
privacy_settings = PrivacySettings()


# Pretty print privacy settings
def print_privacy_settings():
    """Print current privacy settings (for debugging)"""
    print("\n" + "="*70)
    print("[PRIVACY] Privacy Configuration")
    print("="*70)

    summary = privacy_settings.get_privacy_summary()

    print("\n📊 Data Minimization:")
    for key, value in summary["data_minimization"].items():
        icon = "✅" if (value and "delete" in key) or (not value and "store" in key) else "⚠️"
        print(f"  {icon} {key}: {value}")

    print("\n🔒 Processing:")
    for key, value in summary["processing"].items():
        print(f"  • {key}: {value}")

    print("\n👤 User Rights:")
    for key, value in summary["user_rights"].items():
        icon = "✅" if value else "❌"
        print(f"  {icon} {key}: {value}")

    print("\n📋 Consent:")
    for key, value in summary["consent"].items():
        icon = "✅" if value else "⚠️"
        print(f"  {icon} {key}: {value}")

    # Validate for production
    is_valid, warnings = privacy_settings.validate_for_production()

    if is_valid:
        print("\n✅ Privacy configuration is production-ready!")
    else:
        print("\n⚠️ Privacy Warnings:")
        for warning in warnings:
            print(f"  {warning}")

    print("="*70 + "\n")


if __name__ == "__main__":
    # Test privacy settings
    print_privacy_settings()

    # Show recommended config
    print("\n" + "="*70)
    print("RECOMMENDED PRODUCTION CONFIG")
    print("="*70)
    print(privacy_settings.get_recommended_production_config())
