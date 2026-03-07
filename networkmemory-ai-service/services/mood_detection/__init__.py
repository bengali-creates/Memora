"""
Mood Detection Service

Analyzes conversation mood and emotional indicators from transcripts
"""

from .mood_analyzer import MoodAnalyzer, get_mood_analyzer

__all__ = ["MoodAnalyzer", "get_mood_analyzer"]
