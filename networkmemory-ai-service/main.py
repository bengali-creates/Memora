from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time
from datetime import datetime
import httpx
import uuid
import os
import json

from models import (
    AudioProcessRequest,
    AudioProcessResponse,
    HealthResponse
)
from config import settings, print_settings
from audio_pipeline.pipeline import AudioPipeline
from privacy_config import privacy_settings, print_privacy_settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # Alternative docs at /redoc
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins for development
                # In production, specify exact origins:
                # "http://localhost:3000",  # Node.js backend
                # "http://localhost:19000",  # React Native dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# ============================================
# Global State
# ============================================
# Pipeline is initialized on startup and reused for all requests
# This is efficient because:
# - Whisper model loads once (not per request)
# - API clients are reused
# - Saves ~5-10 seconds per request

pipeline = None

# ============================================
# Startup Event
# ============================================

@app.on_event("startup")
async def startup_event():
    """
    Run when server starts

    Initialization:
    1. Print configuration
    2. Validate settings
    3. Load pipeline (Whisper model, etc.)
    """
    global pipeline

    print("\n" + "="*70)
    print("[*] STARTING SERVER")
    print("="*70)

    # Print configuration
    print_settings()

    # Print privacy configuration
    print_privacy_settings()

    # Validate configuration
    try:
        settings.validate()
    except ValueError as e:
        print(f"\n[ERROR] Configuration error: {e}")
        print("Server will start but API calls will fail.")
        print("Please fix your .env file and restart.\n")
        # Don't exit - let server start so user can test /health

    # Initialize pipeline
    print("[INIT] Initializing AI Pipeline...")
    try:
        pipeline = AudioPipeline(debug=settings.DEBUG)
        print("[OK] Pipeline initialized successfully\n")
    except Exception as e:
        print(f"[ERROR] Failed to initialize pipeline: {e}")
        print("Server will start but /api/audio/process will fail.\n")
        # Continue anyway - server can still respond to /health

    print("="*70)
    print("[OK] SERVER READY")
    print("="*70)
    print(f" API: http://{settings.HOST}:{settings.PORT}")
    print(f" Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f" Health: http://{settings.HOST}:{settings.PORT}/health")
    print("="*70 + "\n")


# ============================================
# Root Endpoint
# ============================================

@app.get("/")
async def root():
    """
    Root endpoint - API information

    Useful for:
    - Quick check that server is running
    - Finding other endpoints
    - API version info
    """
    return {
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "process_audio": "/api/audio/process",
            "documentation": "/docs"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================
# Health Check Endpoint
# ============================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Used by:
    - Load balancers
    - Monitoring systems (UptimeRobot, etc.)
    - Person 3's infrastructure checks

    Returns:
    - 200 OK if healthy
    - 503 Service Unavailable if unhealthy (e.g., pipeline not loaded)
    """
    is_healthy = pipeline is not None

    if is_healthy:
        return HealthResponse(
            status="healthy",
            message=f"{settings.APP_NAME} is running",
            version=settings.VERSION,
            timestamp=datetime.utcnow().isoformat()
        )
    else:
        # Return 503 if pipeline failed to initialize
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": "Pipeline not initialized",
                "version": settings.VERSION,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# ============================================
# Main Processing Endpoint
# ============================================

@app.post("/api/audio/process", response_model=AudioProcessResponse)
async def process_audio(request: AudioProcessRequest):
    """
    Process audio file and extract contact information

    This is the MAIN endpoint that Node.js calls

    Flow:
    1. Node.js uploads audio to Supabase Storage
    2. Node.js calls this endpoint with audio URL
    3. We download, process, and extract contact info
    4. Return contact card to Node.js
    5. Node.js stores in database and notifies frontend

    Request body:
        {
            "audio_url": "https://storage.supabase.co/...",
            "event_context": {
                "event_name": "DevFest Kolkata",
                "location": "Kolkata",
                "timestamp": "2026-03-04T15:30:00Z"
            }
        }

    Response:
        {
            "status": "success",
            "contact_card": { ... },
            "metadata": { ... }
        }

    Error handling:
    - 400 Bad Request: Invalid input
    - 500 Internal Server Error: Processing failed
    - 503 Service Unavailable: Pipeline not ready
    """
    # Check pipeline is initialized
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="AI Pipeline not initialized. Check server logs."
        )

    # Log request
    print(f"\n[REQUEST] Received processing request")
    print(f"   Audio URL: {request.audio_url}")
    if request.event_context:
        print(f"   Event: {request.event_context.event_name}")
        print(f"   Location: {request.event_context.location}")

    try:
        # Convert Pydantic model to dict for pipeline
        event_context = None
        if request.event_context:
            event_context = request.event_context.dict()

        # Process through pipeline
        result = await pipeline.process_audio(
            audio_url=request.audio_url,
            event_context=event_context
        )

        # Return response
        if result["status"] == "success":
            return AudioProcessResponse(
                status="success",
                contact_card=result["contact_card"],
                metadata=result["metadata"],
                raw_data=result.get("raw_data")  # Only if debug mode
            )
        else:
            # Processing failed but didn't raise exception
            return AudioProcessResponse(
                status="error",
                error=result["error"],
                metadata=result.get("metadata")
            )

    except Exception as e:
        # Unexpected error
        print(f"\n[ERROR] Processing failed with exception: {str(e)}")

        # Return error response
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )


# ============================================
# Direct Upload Endpoint (NEW - For Frontend)
# ============================================

@app.post("/api/audio/process-upload")
async def process_audio_upload(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    user_id: str = Form(...),
    user_token: str = Form(...)
):
    """
    Direct upload from React Native frontend

    Flow:
    1. Receive audio file from frontend
    2. Process through AI pipeline
    3. Return contact card to frontend immediately (fast response!)
    4. Send to backend in background (async - user doesn't wait)

    This gives the best user experience - fast results!
    """

    print(f"\n[UPLOAD] Received audio from user: {user_id}")
    print(f"   Filename: {audio.filename}")
    print(f"   Content-Type: {audio.content_type}")

    # Check pipeline is initialized
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="AI Pipeline not initialized. Check server logs."
        )

    # Create temp directory
    temp_dir = "/tmp/audio_uploads"
    os.makedirs(temp_dir, exist_ok=True)

    # Generate unique filename
    file_ext = os.path.splitext(audio.filename)[1] or '.wav'
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}{file_ext}")

    # Read and save audio data
    audio_data = await audio.read()

    with open(temp_path, "wb") as f:
        f.write(audio_data)

    print(f"[OK] Audio saved temporarily: {temp_path}")

    try:
        # Process through pipeline
        print("[PROCESSING] Starting AI pipeline...")

        # Check if already WAV - use optimization!
        is_wav = audio.content_type == 'audio/wav' or file_ext.lower() == '.wav'

        if is_wav:
            print("[OPTIMIZATION] File is WAV - will skip conversion!")

        # Step 1: Preprocess (with WAV optimization)
        chunk_paths, prep_metadata = await pipeline.preprocessor.preprocess_file(
            temp_path,
            skip_conversion=is_wav
        )

        if not chunk_paths:
            raise Exception("Preprocessing produced no chunks")

        # Step 2: Diarize
        diarization_result = await pipeline.diarizer.diarize(chunk_paths[0])

        # Step 3: Extract contact info
        contact_card = pipeline.extractor.extract_contact(
            diarization_result["conversation"],
            event_context=None
        )

        contact_card["user_id"] = user_id

        print(f"[OK] Processing complete: {contact_card.get('name', 'Unknown')}")

        # Build result metadata
        result = {
            "contact_card": contact_card,
            "metadata": {
                "processing_time_seconds": prep_metadata.get("duration_seconds", 0),
                "num_speakers": diarization_result.get("num_speakers", 0),
                "conversion_skipped": prep_metadata.get("conversion_skipped", False)
            }
        }

        # Schedule background task to notify backend
        print("[BACKGROUND] Scheduling backend notification...")
        background_tasks.add_task(
            notify_backend_async,
            contact_card=contact_card,
            audio_data=audio_data,
            audio_filename=audio.filename,
            user_id=user_id,
            user_token=user_token,
            metadata=result["metadata"]
        )

        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass

        # Return to frontend immediately
        return {
            "status": "success",
            "contact_card": contact_card,
            "metadata": result["metadata"],
            "message": "Contact card ready! Saving to your account in background..."
        }

    except Exception as e:
        # Clean up on error
        try:
            os.remove(temp_path)
        except:
            pass

        print(f"\n[ERROR] Processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )


async def notify_backend_async(
    contact_card: dict,
    audio_data: bytes,
    audio_filename: str,
    user_id: str,
    user_token: str,
    metadata: dict
):
    """
    Background task: Send contact card + audio to backend
    Runs AFTER response is sent to frontend
    User doesn't wait for this!
    """
    print(f"\n[BACKGROUND] Starting backend notification for: {contact_card.get('name')}")

    try:
        # Prepare multipart form data
        files = {
            'audio': (audio_filename, audio_data, 'audio/wav')
        }

        data = {
            'user_id': user_id,
            'contact_data': json.dumps(contact_card),
            'metadata': json.dumps(metadata)
        }

        headers = {
            'Authorization': f'Bearer {user_token}'
        }

        backend_url = settings.BACKEND_URL or "http://localhost:3000"
        endpoint = f"{backend_url}/api/upload/save-from-python"

        print(f"[BACKGROUND] Sending to backend: {endpoint}")

        # Send to backend with timeout
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                endpoint,
                files=files,
                data=data,
                headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                print(f"[OK] Backend saved contact successfully!")
                print(f"     Contact ID: {result.get('contact_id')}")
                print(f"     Audio URL: {result.get('audio_url', 'N/A')}")
            else:
                print(f"[WARNING] Backend save failed: {response.status_code}")
                print(f"          Response: {response.text[:200]}")

    except httpx.TimeoutException:
        print(f"[WARNING] Backend timeout - will retry later")
        # TODO: Add to retry queue

    except Exception as e:
        print(f"[ERROR] Failed to notify backend: {str(e)}")
        # Log error but don't fail - user already has results!
        # TODO: Add to retry queue or dead letter queue


# ============================================
# Pipeline Info Endpoint (for debugging)
# ============================================

@app.get("/api/pipeline/info")
async def get_pipeline_info():
    """
    Get information about the pipeline configuration

    Useful for debugging and monitoring

    Only available in debug mode
    """
    if not settings.DEBUG:
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only available in debug mode"
        )

    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Pipeline not initialized"
        )

    info = pipeline.get_pipeline_info()
    return {
        "pipeline_info": info,
        "server_config": {
            "debug_mode": settings.DEBUG,
            "host": settings.HOST,
            "port": settings.PORT,
            "whisper_model": settings.WHISPER_MODEL_SIZE,
            "chunk_length": settings.CHUNK_LENGTH_SECONDS
        }
    }


# ============================================
# Privacy Endpoints
# ============================================

@app.get("/api/privacy/settings")
async def get_privacy_settings():
    """
    Get current privacy configuration

    Useful for:
    - Showing users what data is collected
    - Compliance documentation
    - Frontend privacy notices

    Returns:
        Dict with privacy settings summary
    """
    return {
        "privacy_settings": privacy_settings.get_privacy_summary(),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/privacy/delete-user-data")
async def delete_user_data(request: dict):
    """
    Delete all data for a user (DPDP Right to Erasure)

    This is a placeholder - actual implementation should:
    1. Delete contact cards from database
    2. Delete audio files from storage
    3. Log the deletion request
    4. Return confirmation

    Request body:
        {
            "user_id": "8f31600d-a39b-45d4-9625-b9b69bd03126"
        }

    Response:
        {
            "status": "success",
            "message": "All user data has been deleted",
            "deleted_items": {
                "contacts": 15,
                "audio_files": 15
            }
        }
    """
    if not privacy_settings.ENABLE_DATA_DELETION_REQUEST:
        raise HTTPException(
            status_code=403,
            detail="Data deletion is not enabled"
        )

    user_id = request.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id is required"
        )

    # Log deletion request for compliance
    if privacy_settings.LOG_DELETION_REQUESTS:
        print(f"\n[PRIVACY] Data deletion request received for user: {user_id}")
        print(f"   Timestamp: {datetime.utcnow().isoformat()}")

    # TODO: Actual implementation should call backend to delete data
    # For now, this is a placeholder that shows the structure

    return {
        "status": "success",
        "message": "Data deletion request received. Processing will complete within 30 days as per DPDP guidelines.",
        "user_id": user_id,
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "note": "This is a placeholder. Actual implementation should integrate with your database."
    }


@app.get("/api/privacy/data-access")
async def request_data_access(user_id: str):
    """
    Request access to user's data (DPDP Right to Access)

    This is a placeholder - actual implementation should:
    1. Retrieve all contact cards for user
    2. Retrieve metadata about audio processing
    3. Return in portable format (JSON)

    Query parameters:
        user_id: User's ID

    Response:
        {
            "user_id": "...",
            "contacts": [...],
            "processing_history": [...],
            "data_export_format": "JSON"
        }
    """
    if not privacy_settings.ENABLE_DATA_ACCESS_REQUEST:
        raise HTTPException(
            status_code=403,
            detail="Data access requests are not enabled"
        )

    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id parameter is required"
        )

    # Log access request for compliance
    if privacy_settings.LOG_PROCESSING_ACTIVITIES:
        print(f"\n[PRIVACY] Data access request for user: {user_id}")

    # TODO: Actual implementation should retrieve from database
    return {
        "status": "success",
        "user_id": user_id,
        "message": "This is a placeholder. Actual implementation should retrieve user data from your database.",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================
# Agent Endpoints
# ============================================

from agents import enrich_contact, ContactEnrichmentCrew

@app.post("/api/agents/enrich")
async def enrich_contact_endpoint(request: dict):
    """
    Enrich a contact using AI agents

    This endpoint runs multiple AI agents to enrich contact information:
    - LinkedIn Research Agent: Find LinkedIn profile and professional info
    - Follow-up Scheduler Agent: Create optimal follow-up strategy
    - Network Analysis Agent: Analyze network position (requires multiple contacts)

    Request body:
        {
            "contact_data": {
                "name": "Sarah Chen",
                "company": "Google",
                "role": "ML Engineer",
                "topics_discussed": ["AI", "ML"],
                "conversation_summary": "..."
            }
        }

    Response:
        {
            "status": "success",
            "enriched_contact": {...},
            "enrichment_metadata": {...}
        }
    """
    try:
        contact_data = request.get('contact_data')

        if not contact_data:
            raise HTTPException(
                status_code=400,
                detail="contact_data is required"
            )

        print(f"\n[AGENTS] Enriching contact: {contact_data.get('name', 'Unknown')}")

        # Run enrichment
        enriched = enrich_contact(contact_data=contact_data)

        print("[OK] Contact enrichment complete")

        return {
            "status": "success",
            "enriched_contact": enriched,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"\n[ERROR] Contact enrichment failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Enrichment failed: {str(e)}"
        )


@app.post("/api/agents/enrich-batch")
async def enrich_batch_endpoint(request: dict):
    """
    Enrich multiple contacts with network analysis

    This is more powerful than single enrichment because it includes:
    - Individual enrichment for each contact
    - Network-wide analysis
    - Introduction suggestions
    - Key connector identification

    Request body:
        {
            "contacts": [
                {"name": "...", "company": "...", ...},
                {"name": "...", "company": "...", ...}
            ]
        }

    Response:
        {
            "status": "success",
            "enriched_contacts": [...],
            "network_analysis": {...},
            "batch_metadata": {...}
        }
    """
    try:
        contacts = request.get('contacts', [])

        if not contacts or len(contacts) == 0:
            raise HTTPException(
                status_code=400,
                detail="contacts array is required and must not be empty"
            )

        print(f"\n[AGENTS] Batch enrichment for {len(contacts)} contacts")

        # Run batch enrichment
        crew = ContactEnrichmentCrew()
        result = crew.enrich_multiple_contacts(contacts)

        print("[OK] Batch enrichment complete")

        return {
            "status": "success",
            **result,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"\n[ERROR] Batch enrichment failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch enrichment failed: {str(e)}"
        )


@app.post("/api/agents/quick-insights")
async def quick_insights_endpoint(request: dict):
    """
    Get quick insights about a contact without full enrichment

    Useful for:
    - Quick preview in mobile app
    - Real-time suggestions
    - Fast priority assessment

    Request body:
        {
            "contact_data": {
                "name": "Sarah Chen",
                "role": "ML Engineer",
                "company": "Google"
            }
        }

    Response:
        {
            "priority_level": "high",
            "recommended_action": "Send follow-up within 24 hours",
            "connection_value": "high",
            "quick_summary": "..."
        }
    """
    try:
        contact_data = request.get('contact_data')

        if not contact_data:
            raise HTTPException(
                status_code=400,
                detail="contact_data is required"
            )

        crew = ContactEnrichmentCrew()
        insights = crew.get_quick_insights(contact_data)

        return insights

    except Exception as e:
        print(f"\n[ERROR] Quick insights failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Quick insights failed: {str(e)}"
        )


# ============================================
# Exception Handlers
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Catch-all exception handler

    Ensures we always return JSON (never HTML error pages)
    """
    print(f"\n[ERROR] Unhandled exception: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": str(exc),
            "detail": "Internal server error"
        }
    )


# ============================================
# Run Server
# ============================================

if __name__ == "__main__":
    """
    Run with: python main.py

    Or with uvicorn directly:
    uvicorn main:app --reload --port 8000
    """
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG  # Auto-reload on code changes in debug mode
    )
