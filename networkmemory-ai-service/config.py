"""
Configuration settings for NetworkMemory AI Service

Why this approach:
1. Centralized configuration - change once, affect everywhere
2. Environment variables for secrets - never commit API keys
3. Type hints for better IDE support
4. Defaults for development ease
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Application settings loaded from environment variables

    Usage:
        from config import settings
        api_key = settings.GEMINI_API_KEY
    """

    # ============================================
    # API Keys
    # ============================================
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ASSEMBLYAI_API_KEY: str = os.getenv("ASSEMBLYAI_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # ============================================
    # Database
    # ============================================
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # ============================================
    # External Services
    # ============================================
    NODEJS_API_URL: str = os.getenv("NODEJS_API_URL", "http://localhost:3000")

    # Backend URL for direct upload architecture (NEW)
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:3000")

    # ============================================
    # Server Configuration
    # ============================================
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # ============================================
    # Application Metadata
    # ============================================
    APP_NAME: str = "NetworkMemory AI Service"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI service for processing conversations and extracting contact information"

    # ============================================
    # Audio Processing Settings
    # ============================================
    WHISPER_MODEL_SIZE: str = os.getenv("WHISPER_MODEL_SIZE", "base")
    CHUNK_LENGTH_SECONDS: int = int(os.getenv("CHUNK_LENGTH_SECONDS", "90"))

    # ============================================
    # SERVICE SELECTION (Modular Architecture!)
    # Change these to switch models - NO code changes needed!
    # ============================================
    # Transcription: "whisper" (local, free) | "faster-whisper" (faster, local) | "assembly" (API)
    TRANSCRIPTION_SERVICE: str = os.getenv("TRANSCRIPTION_SERVICE", "whisper")

    # Diarization: "assembly" (API, accurate) | "pyannote" (local, free)
    DIARIZATION_SERVICE: str = os.getenv("DIARIZATION_SERVICE", "assembly")

    # Extraction: "gemini" (free tier) | "gpt4" (paid) | "claude" (paid)
    EXTRACTION_SERVICE: str = os.getenv("EXTRACTION_SERVICE", "gemini")

    # ============================================
    # Validation
    # ============================================
    def validate(self) -> bool:
        """
        Validate that required settings are present
        Returns True if valid, raises error if not
        """
        required_keys = {
            "GEMINI_API_KEY": self.GEMINI_API_KEY,
            "ASSEMBLYAI_API_KEY": self.ASSEMBLYAI_API_KEY,
        }

        missing = [key for key, value in required_keys.items() if not value]

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please set them in your .env file"
            )

        return True


# Create global settings instance
settings = Settings()


# Convenience function to check if we're in development
def is_development() -> bool:
    """Check if running in development mode"""
    return settings.DEBUG


# Pretty print settings (without exposing secrets)
def print_settings():
    """Print current settings (sanitized)"""
    print("\n" + "="*60)
    print(f"[CONFIG]  {settings.APP_NAME} v{settings.VERSION}")
    print("="*60)
    print(f"Host: {settings.HOST}:{settings.PORT}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Whisper Model: {settings.WHISPER_MODEL_SIZE}")
    print(f"Chunk Length: {settings.CHUNK_LENGTH_SECONDS}s")
    print(f"Node.js Backend: {settings.NODEJS_API_URL}")

    print(f"\n[SERVICES] Active Services:")
    print(f"  Transcription: {settings.TRANSCRIPTION_SERVICE}")
    print(f"  Diarization: {settings.DIARIZATION_SERVICE}")
    print(f"  Extraction: {settings.EXTRACTION_SERVICE}")

    # Show which API keys are configured (without showing actual keys)
    print(f"\n API Keys:")
    print(f"  Gemini: {' Configured' if settings.GEMINI_API_KEY else '[ERROR] Missing'}")
    print(f"  AssemblyAI: {' Configured' if settings.ASSEMBLYAI_API_KEY else '[ERROR] Missing'}")
    print(f"  ElevenLabs: {' Configured' if settings.ELEVENLABS_API_KEY else '[ERROR] Missing'}")
    print(f"  OpenAI: {' Configured' if settings.OPENAI_API_KEY else '[ERROR] Missing'}")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Test configuration
    print_settings()

    try:
        settings.validate()
        print(" Configuration is valid!")
    except ValueError as e:
        print(f" Configuration error: {e}")
