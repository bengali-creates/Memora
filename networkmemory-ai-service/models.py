"""
Pydantic models for request/response validation

Why Pydantic:
1. Automatic validation - FastAPI validates data before it reaches your code
2. Auto-generated docs - Swagger UI shows exact data structure
3. Type safety - Catch bugs early with type hints
4. Easy serialization - Convert to/from JSON automatically
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============================================
# Request Models
# ============================================

class EventContext(BaseModel):
    """
    Context about the event where conversation happened

    All fields optional because:
    - Event detection might fail
    - User might not provide context
    - Better to process with partial info than fail
    """
    event_name: Optional[str] = Field(None, description="Name of the event (e.g., 'DevFest Kolkata 2026')")
    location: Optional[str] = Field(None, description="Location of the event (e.g., 'Kolkata, India')")
    timestamp: Optional[str] = Field(None, description="ISO 8601 timestamp of when conversation happened")

    class Config:
        json_schema_extra = {
            "example": {
                "event_name": "DevFest Kolkata 2026",
                "location": "Kolkata, India",
                "timestamp": "2026-03-04T15:30:00Z"
            }
        }


class AudioProcessRequest(BaseModel):
    """
    Request to process audio and extract contact information

    This is what Node.js backend will send to us
    """
    audio_url: str = Field(
        ...,  # ... means required
        description="URL to audio file (must be accessible, formats: wav, mp3, m4a)"
    )
    event_context: Optional[EventContext] = Field(
        None,
        description="Optional context about the event"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "audio_url": "https://storage.supabase.co/bucket/audio_123.wav",
                "event_context": {
                    "event_name": "TechCrunch Disrupt 2026",
                    "location": "San Francisco",
                    "timestamp": "2026-03-04T15:30:00Z"
                }
            }
        }


# ============================================
# Response Models
# ============================================

class ContactCard(BaseModel):
    """
    Extracted contact information

    Why these fields:
    - name: Most important - who did you meet?
    - role/company: Context about the person
    - topics_discussed: What did you talk about? (for search)
    - follow_ups: Action items (for reminders)
    - confidence_score: How sure are we? (for UI indicators)
    """
    name: Optional[str] = Field(None, description="Person's full name")
    role: Optional[str] = Field(None, description="Job title or role")
    company: Optional[str] = Field(None, description="Company or organization")
    location: Optional[str] = Field(None, description="City or region they're from")
    phone: Optional[str] = Field(None, description="Phone number if mentioned")
    email: Optional[str] = Field(None, description="Email if mentioned")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn URL if mentioned")

    topics_discussed: List[str] = Field(
        default_factory=list,
        description="Array of topics discussed (e.g., ['AI safety', 'Startups'])"
    )
    follow_ups: List[str] = Field(
        default_factory=list,
        description="Action items mentioned (e.g., ['Send GitHub repo', 'Connect on LinkedIn'])"
    )

    conversation_summary: str = Field(
        ...,
        description="2-3 sentence summary of the conversation"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,  # greater than or equal to 0
        le=1.0,  # less than or equal to 1
        description="Confidence in extraction quality (0.0 to 1.0)"
    )

    # Metadata added by our system
    met_at: Optional[str] = Field(None, description="Event name where they met")
    met_date: Optional[str] = Field(None, description="Date of meeting")
    met_location: Optional[str] = Field(None, description="Location of meeting")
    raw_conversation: Optional[str] = Field(None, description="Full diarized conversation text")
    extraction_time: Optional[float] = Field(None, description="Time taken to extract (seconds)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sarah Chen",
                "role": "ML Engineer",
                "company": "Google",
                "location": "Mountain View",
                "topics_discussed": ["AI safety", "LLM alignment", "Interpretability"],
                "follow_ups": ["Connect on LinkedIn", "Send research papers"],
                "conversation_summary": "Discussed AI safety work at Google focusing on LLM alignment and interpretability. Sarah offered to share research papers and mentioned hiring opportunities.",
                "confidence_score": 0.87,
                "met_at": "DevFest Kolkata 2026"
            }
        }


class ProcessingMetadata(BaseModel):
    """
    Metadata about the processing pipeline

    Useful for:
    - Performance monitoring
    - Debugging
    - Showing user "what happened"

    Note: Some fields are optional because they may not be available if processing fails early
    """
    audio_duration: Optional[float] = Field(None, description="Duration of audio in seconds")
    num_speakers: Optional[int] = Field(None, description="Number of speakers detected")
    processing_time: float = Field(..., description="Total processing time in seconds")
    utterances_count: Optional[int] = Field(None, description="Number of conversational turns")


class RawData(BaseModel):
    """
    Raw processing results for debugging

    Only included if debug mode is on
    """
    full_transcription: Optional[str] = None
    diarized_conversation: Optional[str] = None
    utterances: Optional[List[Dict[str, Any]]] = None


class AudioProcessResponse(BaseModel):
    """
    Response from audio processing

    Two possible states:
    1. Success: status="success", contact_card present
    2. Error: status="error", error message present
    """
    status: str = Field(..., description="'success' or 'error'")
    contact_card: Optional[ContactCard] = Field(None, description="Extracted contact information")
    metadata: Optional[ProcessingMetadata] = Field(None, description="Processing metadata")
    raw_data: Optional[RawData] = Field(None, description="Raw processing data (debug only)")
    error: Optional[str] = Field(None, description="Error message if processing failed")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "contact_card": {
                    "name": "Sarah Chen",
                    "role": "ML Engineer",
                    "company": "Google",
                    "confidence_score": 0.87
                },
                "metadata": {
                    "processing_time": 18.5,
                    "num_speakers": 2,
                    "audio_duration": 120.0,
                    "utterances_count": 24
                }
            }
        }


# ============================================
# Health Check Model
# ============================================

class HealthResponse(BaseModel):
    """Simple health check response"""
    status: str = Field(..., description="'healthy' or 'unhealthy'")
    message: str
    version: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "NetworkMemory AI Service is running",
                "version": "1.0.0",
                "timestamp": "2026-03-04T12:00:00Z"
            }
        }
