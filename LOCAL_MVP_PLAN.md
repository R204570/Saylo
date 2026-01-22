# LOCAL MVP IMPLEMENTATION PLAN
## Hardware-Optimized AI Interview Platform

### 🎯 MVP SCOPE
**Goal**: Single working interview session with AI voice interviewer

**What's Included**:
- ✅ One user account (no auth for MVP)
- ✅ One subject (e.g., "Software Engineer Interview")
- ✅ One resume upload & parsing
- ✅ One reference document (PDF)
- ✅ Real-time AI voice conversation
- ✅ Resume-aware question generation
- ✅ Context-aware assistance
- ✅ Basic proctoring (face detection)
- ✅ Session transcript
- ✅ Simple analytics report

**What's Excluded** (for now):
- ❌ Multi-user authentication
- ❌ Multiple subjects
- ❌ MCQ popups
- ❌ Advanced proctoring
- ❌ Complex analytics dashboard

---

## 🏗️ ARCHITECTURE (LOCAL-FIRST)

```
┌─────────────────────────────────────────────┐
│         Frontend (Simple HTML/JS)           │
│         localhost:8080                      │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│      FastAPI Backend (localhost:8000)       │
│  - Session management                       │
│  - File upload/processing                   │
│  - API endpoints                            │
└─────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Ollama     │ │  ChromaDB    │ │  PostgreSQL  │
│ localhost    │ │  (local)     │ │  (local)     │
│  :11434      │ │              │ │  :5432       │
└──────────────┘ └──────────────┘ └──────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│         LiveKit (Self-Hosted)               │
│         localhost:7880                      │
└─────────────────────────────────────────────┘
```

---

## 🧠 AI MODEL SELECTION (VRAM-OPTIMIZED)

### Primary Models (Total VRAM: ~3.5GB)
1. **LLM**: `llama3.1:8b-instruct-q4_K_M` (~4.5GB on disk, ~3GB VRAM)
   - Question generation
   - Answer evaluation
   - Context-aware responses

2. **Embeddings**: `nomic-embed-text` (CPU-based, ~300MB)
   - Document vectorization
   - Semantic search

3. **STT**: `whisper-small` (CPU-based, ~500MB)
   - Speech-to-text transcription
   - Runs on CPU to save VRAM

4. **TTS**: `piper-tts` (CPU-based, ~50MB)
   - Text-to-speech for AI voice
   - Fast, local, CPU-based

5. **Vision** (Optional): `llava:7b-q4` (~4GB)
   - Face detection for proctoring
   - **Strategy**: Run ONLY when LLM is idle
   - Sample 1 frame every 5 seconds

### VRAM Management Strategy
- **Sequential Processing**: Never run LLM + Vision simultaneously
- **Model Unloading**: Unload vision model after frame processing
- **CPU Offloading**: Use CPU for embeddings, STT, TTS
- **Batch Processing**: Process vision frames in batches during pauses

---

## 📁 PROJECT STRUCTURE

```
Saylo/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Configuration
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── session.py
│   │   │   ├── transcript.py
│   │   │   └── analytics.py
│   │   ├── services/               # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── ollama_service.py   # Ollama integration
│   │   │   ├── vector_service.py   # ChromaDB operations
│   │   │   ├── document_service.py # PDF processing
│   │   │   ├── stt_service.py      # Whisper STT
│   │   │   ├── tts_service.py      # Piper TTS
│   │   │   ├── vision_service.py   # Face detection
│   │   │   └── livekit_service.py  # LiveKit integration
│   │   ├── api/                    # API routes
│   │   │   ├── __init__.py
│   │   │   ├── session.py
│   │   │   ├── upload.py
│   │   │   └── interview.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── pdf_parser.py
│   │       └── resume_parser.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── app.js
│   │   ├── livekit-client.js
│   │   └── interview.js
│   └── assets/
├── data/
│   ├── uploads/                    # Resume & docs
│   ├── chromadb/                   # Vector storage
│   └── recordings/                 # Session recordings
├── scripts/
│   ├── setup_local.sh              # Linux/Mac setup
│   ├── setup_local.ps1             # Windows setup
│   ├── start_services.sh
│   └── start_services.ps1
├── docker/
│   ├── docker-compose.yml          # All services
│   ├── postgres/
│   └── livekit/
├── models/                         # Downloaded models
│   ├── ollama/
│   ├── whisper/
│   └── piper/
├── Developement.txt
├── README.md
└── LOCAL_MVP_PLAN.md
```

---

## 🔧 SETUP SEQUENCE

### Step 1: Install Dependencies (Windows)
```powershell
# Python 3.11
# PostgreSQL 15
# Ollama
# FFmpeg (for audio processing)
```

### Step 2: Download Models
```bash
# Ollama models
ollama pull llama3.1:8b-instruct-q4_K_M
ollama pull nomic-embed-text

# Whisper (via faster-whisper)
# Auto-downloads on first use

# Piper TTS
# Auto-downloads on first use
```

### Step 3: Initialize Databases
```sql
-- PostgreSQL schema
-- ChromaDB auto-initializes
```

### Step 4: Start Services
```powershell
# Terminal 1: Ollama (if not running as service)
ollama serve

# Terminal 2: PostgreSQL (if not running as service)
# Usually runs as Windows service

# Terminal 3: Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 4: Frontend (simple HTTP server)
cd frontend
python -m http.server 8080

# Terminal 5: LiveKit (Docker)
docker-compose up livekit
```

---

## 🎬 MVP WORKFLOW

### 1. **Setup Phase** (One-time)
```
User → Upload Resume (PDF) → Backend parses → Store in DB
User → Upload Reference Doc (PDF) → Backend chunks → Store in ChromaDB
```

### 2. **Interview Session Start**
```
User → Click "Start Interview" → Backend:
  - Create session record (PostgreSQL)
  - Create LiveKit room
  - Load resume context
  - Generate first question (Ollama)
  - Return room token to frontend
```

### 3. **Real-time Interview Loop**
```
Frontend connects to LiveKit room
↓
AI Agent joins room (backend)
↓
AI speaks first question (TTS → LiveKit audio track)
↓
User speaks answer → LiveKit captures audio
↓
Backend receives audio → Whisper STT → Text
↓
Text → Ollama (evaluate + generate next question)
↓
Response → TTS → LiveKit audio
↓
Repeat 5-10 questions
```

### 4. **Proctoring** (Background)
```
Every 5 seconds:
  - Capture 1 frame from user video
  - If LLM idle: Run face detection (llava)
  - Log anomalies (no face, multiple faces)
  - Store in DB
```

### 5. **Session End**
```
User → Click "End Interview"
↓
Backend:
  - Stop LiveKit room
  - Generate transcript (from stored text)
  - Calculate basic scores
  - Generate analytics report
  - Display to user
```

---

## 📊 ANALYTICS (MVP)

### Simple Metrics:
1. **Duration**: Total session time
2. **Questions Answered**: Count
3. **Average Response Time**: Per question
4. **Proctoring Flags**: Count of anomalies
5. **Transcript**: Full conversation text
6. **Key Topics**: Extracted from questions (using embeddings)

### Report Format (JSON):
```json
{
  "session_id": "uuid",
  "duration_seconds": 1200,
  "questions_count": 8,
  "avg_response_time": 45,
  "proctoring_flags": 2,
  "topics_covered": ["Python", "System Design", "Algorithms"],
  "transcript": [...],
  "recommendations": "Focus on system design concepts"
}
```

---

## ⚡ PERFORMANCE OPTIMIZATIONS

### 1. **VRAM Management**
- Load LLM on startup, keep in memory
- Unload vision model after each use
- Use CPU for embeddings/STT/TTS

### 2. **Latency Reduction**
- Pre-generate 2-3 questions ahead
- Cache common prompts
- Use streaming for LLM responses
- Async processing everywhere

### 3. **Context Window**
- Max 2000 tokens per prompt
- Include: Last 2 Q&A + Resume snippet + Retrieved docs (top 3)
- Aggressive summarization

### 4. **Frame Processing**
- 1 frame / 5 seconds (not every frame)
- Resize to 224x224 before vision model
- Skip if LLM busy

---

## 🚀 IMPLEMENTATION PHASES

### Phase 1: Core Backend (Day 1-2)
- [ ] FastAPI setup
- [ ] PostgreSQL schema
- [ ] Basic API endpoints
- [ ] File upload handling

### Phase 2: AI Integration (Day 3-4)
- [ ] Ollama service wrapper
- [ ] ChromaDB integration
- [ ] Document processing pipeline
- [ ] Resume parsing

### Phase 3: Real-time Features (Day 5-6)
- [ ] LiveKit integration
- [ ] STT service (Whisper)
- [ ] TTS service (Piper)
- [ ] Audio streaming

### Phase 4: Interview Logic (Day 7-8)
- [ ] Question generation
- [ ] Answer evaluation
- [ ] Conversation flow
- [ ] Session management

### Phase 5: Frontend (Day 9-10)
- [ ] Simple UI
- [ ] LiveKit client
- [ ] File upload interface
- [ ] Interview interface

### Phase 6: Proctoring (Day 11)
- [ ] Vision service
- [ ] Face detection
- [ ] Anomaly logging

### Phase 7: Analytics (Day 12)
- [ ] Transcript generation
- [ ] Score calculation
- [ ] Report generation

### Phase 8: Testing & Polish (Day 13-14)
- [ ] End-to-end testing
- [ ] Performance tuning
- [ ] Bug fixes
- [ ] Documentation

---

## 🎯 SUCCESS CRITERIA

### MVP is successful if:
1. ✅ User can upload resume + reference doc
2. ✅ AI generates relevant questions based on resume
3. ✅ Real-time voice conversation works (< 5s latency)
4. ✅ Transcription is accurate (> 85%)
5. ✅ Basic face detection works
6. ✅ Session completes without crashes
7. ✅ Analytics report is generated
8. ✅ VRAM stays under 3.8GB
9. ✅ System runs smoothly on target hardware

---

## 🔄 NEXT STEPS AFTER MVP

Once MVP is stable:
1. Add MCQ popup system
2. Improve proctoring (gaze detection, tab switching)
3. Add multiple subjects
4. Implement user authentication
5. Enhanced analytics dashboard
6. Question difficulty calibration
7. Multi-language support
8. Mobile app

---

## 📝 NOTES

- **No Cloud Dependencies**: Everything runs locally
- **Internet Only For**: LiveKit signaling (can be self-hosted), model downloads
- **Fallbacks**: If vision model too slow, disable proctoring
- **Debugging**: Extensive logging for troubleshooting
- **Scalability**: Architecture supports future cloud deployment

---

**Let's build this step by step! 🚀**
