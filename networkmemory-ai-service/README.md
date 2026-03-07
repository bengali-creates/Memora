# NetworkMemory AI Service

**The AI brain for NetworkMemory - processes conversations and extracts contact information**

---

## 🎯 What This Does

This service takes audio recordings of networking conversations and automatically extracts structured contact information.

**Input:** Audio file URL + event context
**Output:** Contact card with name, role, company, topics discussed, follow-ups, etc.

**Processing Pipeline:**
```
Audio URL → Download → Clean → Diarize → Extract → Contact Card
```

---

## 🚀 Quick Start (5 Minutes)

### 1. Clone and Setup

```bash
# Navigate to project directory
cd networkmemory-ai-service

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Get API Keys

You need API keys for these services (all have free tiers):

| Service | Purpose | Get Key | Free Tier |
|---------|---------|---------|-----------|
| Gemini | Contact extraction | https://makersuite.google.com/app/apikey | 1500 requests/day |
| AssemblyAI | Speaker diarization | https://www.assemblyai.com/ | 5 hours/month |
| ElevenLabs | Text-to-speech | https://elevenlabs.io/ | 10k chars/month |
| OpenAI | Embeddings | https://platform.openai.com/api-keys | Pay as you go (~$0.0001/call) |

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
# Use your favorite editor (nano, vim, VS Code, etc.)
nano .env
```

### 4. Test API Connections

```bash
# This verifies all your API keys work
python tests/test_apis.py
```

You should see:
```
✅ PASS - Gemini
✅ PASS - AssemblyAI
✅ PASS - ElevenLabs
✅ PASS - OpenAI Embeddings

🎉 ALL TESTS PASSED!
```

### 5. Start the Server

```bash
# Start FastAPI server
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --port 8000
```

Server starts at: `http://localhost:8000`

### 6. Test the API

Open your browser to: http://localhost:8000/docs

You'll see interactive API documentation (Swagger UI).

Try the `/health` endpoint - should return `{"status": "healthy"}`

---

## 📋 Development Guidelines

This project includes a [`.claude_code`](.claude_code) file with comprehensive coding rules and best practices.

**Key Rules:**
1. **Security**: Never hardcode API keys or sensitive data - always use environment variables
2. **Code Updates**: Prefer updating existing functions over complete rewrites
3. **Tech Stack**: Strictly follow FastAPI, async/await patterns, and defined libraries
4. **Testing**: Write tests for new features and run them before committing

**For AI Assistants & Developers:**
- Read [`.claude_code`](.claude_code) before making changes
- Follow async/await patterns for all I/O operations
- Use type hints and docstrings for all functions
- Handle errors gracefully with proper logging
- Clean up temporary files and resources

---

## 📁 Project Structure

```
networkmemory-ai-service/
├── main.py                      # FastAPI server (HTTP interface)
├── config.py                    # Configuration management
├── models.py                    # Pydantic models (request/response validation)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .env                         # Your actual API keys (not committed)
├── .claude_code                 # Coding rules & guidelines (read this first!)
├── .gitignore                   # Files to ignore in git
│
├── audio_pipeline/              # Audio processing modules
│   ├── __init__.py
│   ├── preprocessing.py         # Download, convert, clean, chunk audio
│   ├── transcription.py         # Speech-to-text with Whisper
│   ├── diarization.py           # Speaker separation with AssemblyAI
│   ├── extraction.py            # Contact extraction with Gemini
│   └── pipeline.py              # Main orchestrator
│
├── utils/                       # Utility functions
│   ├── __init__.py
│   └── helpers.py               # Helper functions
│
└── tests/                       # Test scripts
    ├── __init__.py
    ├── test_apis.py             # Test API connections
    └── test_pipeline.py         # Test complete pipeline
```

---

## 🔧 How It Works (Technical Deep Dive)

### Module 1: Audio Preprocessing

**File:** `audio_pipeline/preprocessing.py`

**What it does:**
1. Downloads audio from URL (Supabase storage)
2. Converts to WAV format (mono, 16kHz)
3. Applies noise reduction (conferences are noisy!)
4. Chunks into 90-second segments

**Why:**
- WAV is standard for speech recognition
- Mono 16kHz is optimal for speech (reduces file size, same accuracy)
- Noise reduction improves transcription accuracy
- Chunking helps with long conversations and rate limits

**Test it:**
```bash
python -m audio_pipeline.preprocessing
```

---

### Module 2: Transcription

**File:** `audio_pipeline/transcription.py`

**What it does:**
- Converts speech to text using faster-whisper
- Segments by natural pauses
- Auto-detects language

**Why faster-whisper:**
- FREE (no API costs)
- 4x faster than original Whisper
- Runs locally (private)
- "base" model: good balance of speed and accuracy

**Model sizes:**
- `tiny`: Fastest, lowest accuracy
- `base`: ⭐ RECOMMENDED - good balance
- `small`: Better accuracy, 2x slower
- `medium`: High accuracy, 4x slower
- `large`: Overkill for networking conversations

**Test it:**
```bash
python -m audio_pipeline.transcription
```

---

### Module 3: Speaker Diarization

**File:** `audio_pipeline/diarization.py`

**What it does:**
- Separates speakers in conversation
- Labels each utterance with speaker ID
- Formats as: "Speaker A: ...\nSpeaker B: ..."

**Why diarization is critical:**
- Need to know WHO said WHAT
- "I work at Google" - was it the user or the contact?
- Helps extract correct person's information

**Why AssemblyAI:**
- Best free diarization API (5 hours/month)
- More accurate than open-source alternatives
- Simple API, well-documented

**Test it:**
```bash
python -m audio_pipeline.diarization
```

---

### Module 4: Contact Extraction

**File:** `audio_pipeline/extraction.py`

**What it does:**
- Extracts structured contact info from conversation
- Uses Gemini 2.0 Flash with carefully crafted prompt
- Returns JSON with name, role, company, topics, follow-ups

**Why Gemini:**
- FREE (1500 requests/day)
- FAST (1-2 second responses)
- SMART (excellent at structured extraction)
- Reliable JSON output

**The Prompt:**
This is the most important part! The prompt tells Gemini:
1. What to extract (name, role, company, etc.)
2. What NOT to do (don't infer, don't guess)
3. How to handle missing data (use null)
4. How to calculate confidence scores
5. Examples of good extractions

**Test it:**
```bash
python -m audio_pipeline.extraction
```

---

### Module 5: Complete Pipeline

**File:** `audio_pipeline/pipeline.py`

**What it does:**
- Orchestrates all modules in sequence
- Handles errors gracefully
- Tracks performance metrics
- Returns structured results

**Flow:**
```
1. Preprocessing → clean audio chunks
2. Diarization → "Speaker A: ..., Speaker B: ..."
3. Extraction → Contact card JSON
4. Return results
```

**Test it:**
```bash
python -m audio_pipeline.pipeline
```

---

## 🌐 API Endpoints

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "NetworkMemory AI Service is running",
  "version": "1.0.0",
  "timestamp": "2026-03-04T12:00:00Z"
}
```

---

### `POST /api/audio/process`

**Main endpoint** - Process audio and extract contact.

**Request:**
```json
{
  "audio_url": "https://storage.supabase.co/bucket/audio_123.wav",
  "event_context": {
    "event_name": "DevFest Kolkata 2026",
    "location": "Kolkata, India",
    "timestamp": "2026-03-04T15:30:00Z"
  }
}
```

**Response (Success):**
```json
{
  "status": "success",
  "contact_card": {
    "name": "Sarah Chen",
    "role": "ML Engineer",
    "company": "Google",
    "location": "Mountain View",
    "topics_discussed": ["AI safety", "LLM alignment"],
    "follow_ups": ["Connect on LinkedIn", "Send research papers"],
    "conversation_summary": "Discussed AI safety work...",
    "confidence_score": 0.87,
    "met_at": "DevFest Kolkata 2026"
  },
  "metadata": {
    "audio_duration": 120.5,
    "num_speakers": 2,
    "processing_time": 18.3,
    "utterances_count": 24
  }
}
```

**Response (Error):**
```json
{
  "status": "error",
  "error": "Audio download failed: Connection timeout",
  "metadata": {
    "processing_time": 5.2
  }
}
```

---

### `GET /api/pipeline/info`

Get pipeline configuration (debug mode only).

**Response:**
```json
{
  "pipeline_info": {
    "whisper_model": "base",
    "chunk_length": 90,
    "debug_mode": true
  },
  "server_config": {
    "host": "0.0.0.0",
    "port": 8000
  }
}
```

---

## 🧪 Testing

### Test Individual Modules

```bash
# Test preprocessing
python -m audio_pipeline.preprocessing

# Test transcription
python -m audio_pipeline.transcription

# Test diarization
python -m audio_pipeline.diarization

# Test extraction
python -m audio_pipeline.extraction

# Test complete pipeline
python -m audio_pipeline.pipeline
```

### Test API Connections

```bash
# Verify all API keys work
python tests/test_apis.py
```

### Test with cURL

```bash
# Health check
curl http://localhost:8000/health

# Process audio
curl -X POST http://localhost:8000/api/audio/process \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://storage.googleapis.com/aai-docs-samples/espn.m4a",
    "event_context": {
      "event_name": "DevFest Kolkata 2026",
      "location": "Kolkata",
      "timestamp": "2026-03-04T15:30:00Z"
    }
  }'
```

---

## ⚙️ Configuration

All configuration is in `.env` file.

**Key settings:**

```bash
# Model sizes
WHISPER_MODEL_SIZE=base  # tiny, base, small, medium, large
CHUNK_LENGTH_SECONDS=90   # Audio chunk length

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True  # Enable debug mode (includes raw data in responses)
```

To change Whisper model:
```bash
# In .env
WHISPER_MODEL_SIZE=small  # Better accuracy, slower
```

---

## 🚨 Troubleshooting

### "Module not found" errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### "API key not found" errors

```bash
# Check .env file exists
ls -la .env

# Check API keys are set
cat .env | grep API_KEY

# Restart server after changing .env
```

### "ffmpeg not found" error

```bash
# Mac
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Slow processing

```bash
# Use smaller Whisper model
# In .env:
WHISPER_MODEL_SIZE=tiny  # or base

# Reduce chunk length
CHUNK_LENGTH_SECONDS=60
```

### Out of memory

```bash
# Use smaller Whisper model
WHISPER_MODEL_SIZE=tiny

# Process shorter audio files
# Or chunk into smaller pieces
```

---

## 📊 Performance

**Expected processing times** (on typical laptop CPU):

| Audio Length | Processing Time | Notes |
|--------------|-----------------|-------|
| 30 seconds   | ~8 seconds      | Short intro |
| 60 seconds   | ~12 seconds     | Quick chat |
| 120 seconds  | ~18 seconds     | ⭐ Typical networking conversation |
| 300 seconds  | ~35 seconds     | Long conversation |

**Bottlenecks:**
1. **Diarization** (30-40% of time) - AssemblyAI processes remotely
2. **Transcription** (30-40% of time) - Whisper runs locally
3. **Download** (10-20% of time) - Depends on network
4. **Extraction** (5-10% of time) - Gemini is very fast

**Optimization tips:**
- Use `WHISPER_MODEL_SIZE=tiny` for 2x speedup (slight accuracy loss)
- Shorter audio = faster processing
- Good internet connection helps (download + AssemblyAI)

---

## 🔐 Security Notes

- **API keys**: Never commit `.env` file to git
- **Audio files**: Temporarily stored, automatically cleaned up
- **Data privacy**: All processing is ephemeral (nothing persisted here)
- **CORS**: Configured for development, restrict in production

---

## 🤝 Integration with Node.js Backend

**Person 3 (Node.js) calls this service:**

```javascript
// Node.js backend
const response = await axios.post('http://localhost:8000/api/audio/process', {
  audio_url: 'https://storage.supabase.co/audio_123.wav',
  event_context: {
    event_name: 'DevFest Kolkata',
    location: 'Kolkata',
    timestamp: new Date().toISOString()
  }
});

const contactCard = response.data.contact_card;
// Store in database, emit Socket.io event, etc.
```

---

## 📝 Next Steps (Day 2 & 3)

After Day 1 is complete, we'll add:

**Day 2:**
- Agent system (CrewAI)
- Voice interface (Whisper STT + ElevenLabs TTS)
- Auto-reply bot

**Day 3:**
- Calendar integration
- LinkedIn monitoring
- Pre-meeting briefs

---

## 🆘 Need Help?

1. **Check logs** - Server prints detailed logs
2. **Test individual modules** - Isolate the problem
3. **Verify API keys** - Run `python tests/test_apis.py`
4. **Check Swagger UI** - http://localhost:8000/docs

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Gemini API Guide](https://ai.google.dev/tutorials/python_quickstart)
- [AssemblyAI Docs](https://www.assemblyai.com/docs)
- [Whisper Documentation](https://github.com/openai/whisper)

---

Made with ❤️ for NetworkMemory AI Hackathon
