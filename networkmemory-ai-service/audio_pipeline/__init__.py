"""
Audio Processing Pipeline Package

This package contains all modules for processing audio:
- preprocessing: Download, convert, clean, chunk audio
- transcription: Speech-to-text with Whisper
- diarization: Speaker separation with AssemblyAI
- extraction: Contact info extraction with Gemini
- pipeline: Main orchestrator that combines everything
"""

from .pipeline import AudioPipeline

__all__ = ['AudioPipeline']
