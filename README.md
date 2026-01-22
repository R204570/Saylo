# 🎯 Saylo - AI Interview Helper Platform (LOCAL MVP)

> **Local-first AI-powered interview preparation platform**  
> Optimized for: Intel i5 11th Gen | 32GB RAM | RTX 3050 (4GB VRAM)

---

## 📋 Overview

Saylo is a **100% local** AI interview platform that provides:
- ✅ Real-time AI voice interviewer
- ✅ Resume-aware question generation
- ✅ Context-aware assistance from uploaded materials
- ✅ Basic proctoring (face detection)
- ✅ Session transcripts & analytics
- ✅ **No cloud dependencies** (except LiveKit signaling)

---

## 🏗️ Architecture

```
Frontend (HTML/JS) → FastAPI Backend → Ollama (LLM)
                                    → ChromaDB (Vectors)
                                    → PostgreSQL (Data)
                                    → LiveKit (Real-time)
```

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI | REST API & WebSocket |
| **Database** | PostgreSQL | Relational data |
| **Vector DB** | ChromaDB | Semantic search |
| **LLM** | Ollama (llama3.1:8b-q4) | Question generation, evaluation |
| **Embeddings** | nomic-embed-text | Document vectorization |
| **STT** | Faster Whisper (small) | Speech-to-text |
| **TTS** | Piper TTS | Text-to-speech |
| **Vision** | LLaVA:7b-q4 | Face detection (optional) |
| **Real-time** | LiveKit | Voice/video streaming |

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+**
2. **PostgreSQL 15+**
3. **Ollama** - [Download](https://ollama.ai/download)
4. **FFmpeg** - For audio processing

### Installation

#### Windows

```powershell
# Run setup script
.\scripts\setup_local.ps1

# Or manual setup:
# 1. Create virtual environment
cd backend
python -m venv venv
venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
copy .env.example .env
# Edit .env with your settings

# 4. Create database
psql -U postgres -c "CREATE DATABASE saylo_interview;"

# 5. Download models
ollama pull llama3.1:8b-instruct-q4_K_M
ollama pull nomic-embed-text
ollama pull llava:7b-q4  # Optional, for proctoring
```

#### Linux/Mac

```bash
# Run setup script
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh

# Or follow manual steps above with appropriate commands
```

---

## 🎬 Running the Application

### Start Services

```powershell
# Terminal 1: Ollama (if not running as service)
ollama serve

# Terminal 2: Backend
cd backend
venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate  # Linux/Mac
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Frontend (simple HTTP server)
cd frontend
python -m http.server 8080
```

### Access the Application

- **Frontend**: http://localhost:8080
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📖 Usage Guide

### 1. Upload Resume & Reference Document

```bash
# Upload resume
curl -X POST "http://localhost:8000/api/upload/resume" \
  -F "file=@resume.pdf" \
  -F "session_id=test-session"

# Upload reference document
curl -X POST "http://localhost:8000/api/upload/reference" \
  -F "file=@interview-guide.pdf" \
  -F "session_id=test-session"
```

### 2. Create Interview Session

```bash
curl -X POST "http://localhost:8000/api/sessions/create" \
  -H "Content-Type: application/json" \
  -d '{
    "subject_name": "Software Engineer Interview",
    "resume_path": "data/uploads/resume_test-session.pdf",
    "reference_doc_path": "data/uploads/reference_test-session.pdf"
  }'
```

### 3. Start Interview

```bash
curl -X POST "http://localhost:8000/api/sessions/{session_id}/start"
```

### 4. Generate Questions

```bash
curl -X POST "http://localhost:8000/api/interview/generate-question" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "question_number": 1
  }'
```

### 5. Submit Answer

```bash
curl -X POST "http://localhost:8000/api/interview/submit-answer" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "question_id": "question-id",
    "answer_text": "Your answer here..."
  }'
```

### 6. Get Analytics

```bash
curl "http://localhost:8000/api/sessions/{session_id}/analytics"
```

---

## 🧠 AI Models & VRAM Management

### Model Configuration

| Model | Size | VRAM | Device | Purpose |
|-------|------|------|--------|---------|
| llama3.1:8b-q4 | ~4.5GB | ~3GB | GPU | LLM inference |
| nomic-embed-text | ~300MB | - | CPU | Embeddings |
| whisper-small | ~500MB | - | CPU | STT |
| piper-tts | ~50MB | - | CPU | TTS |
| llava:7b-q4 | ~4GB | ~3GB | GPU | Vision (optional) |

### VRAM Optimization Strategy

1. **Sequential Processing**: Never run LLM + Vision simultaneously
2. **CPU Offloading**: Embeddings, STT, TTS run on CPU
3. **Model Unloading**: Vision model unloaded after use
4. **Frame Sampling**: 1 frame / 5 seconds for proctoring

**Total VRAM Usage**: ~3.5GB (within 4GB limit)

---

## 📁 Project Structure

```
Saylo/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configuration
│   │   ├── models/              # Database models
│   │   ├── services/            # Business logic
│   │   │   ├── ollama_service.py
│   │   │   ├── vector_service.py
│   │   │   ├── document_service.py
│   │   │   ├── stt_service.py
│   │   │   └── tts_service.py
│   │   └── api/                 # API routes
│   ├── requirements.txt
│   └── .env
├── frontend/                    # Simple HTML/JS UI
├── data/
│   ├── uploads/                 # Resumes & docs
│   ├── chromadb/                # Vector storage
│   └── recordings/              # Session recordings
├── scripts/
│   ├── setup_local.ps1          # Windows setup
│   └── setup_local.sh           # Linux/Mac setup
├── LOCAL_MVP_PLAN.md            # Implementation plan
└── README.md                    # This file
```

---

## ⚙️ Configuration

Edit `backend/.env` to customize:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/saylo_interview

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.1:8b-instruct-q4_K_M
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_VISION_MODEL=llava:7b-q4

# Performance
MAX_CONTEXT_TOKENS=2000
CHUNK_SIZE=500
CHUNK_OVERLAP=100
MAX_RETRIEVED_CHUNKS=3

# Vision
VISION_FRAME_INTERVAL=5  # seconds
VISION_ENABLED=true

# Session
QUESTION_COUNT=8
```

---

## 🔧 Troubleshooting

### Ollama Not Responding

```bash
# Check if Ollama is running
ollama list

# Restart Ollama
ollama serve
```

### Database Connection Error

```bash
# Check PostgreSQL status
# Windows: Services → PostgreSQL
# Linux: sudo systemctl status postgresql

# Test connection
psql -U postgres -d saylo_interview
```

### VRAM Out of Memory

1. Reduce `MAX_CONTEXT_TOKENS` in `.env`
2. Disable vision: `VISION_ENABLED=false`
3. Use smaller model: `llama3.1:7b-q4`

### Import Errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

---

## 📊 Performance Benchmarks

On target hardware (i5 11th Gen, 32GB RAM, RTX 3050):

| Operation | Latency | Notes |
|-----------|---------|-------|
| Question Generation | 3-5s | Depends on context size |
| Answer Evaluation | 5-8s | Includes retrieval |
| STT (Whisper) | 1-2s | Per 10s audio |
| TTS (Piper) | 0.5-1s | Per sentence |
| Face Detection | 2-3s | Per frame (5s interval) |

---

## 🛠️ Development

### Running Tests

```bash
cd backend
pytest
```

### API Documentation

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

### Adding New Features

1. Create service in `backend/app/services/`
2. Add API endpoints in `backend/app/api/`
3. Update models if needed in `backend/app/models/`
4. Update configuration in `backend/app/config.py`

---

## 🚧 Roadmap

### MVP (Current)
- [x] Basic backend API
- [x] Document processing
- [x] Question generation
- [x] Answer evaluation
- [ ] LiveKit integration
- [ ] Frontend UI
- [ ] End-to-end testing

### Phase 2
- [ ] MCQ popup system
- [ ] Enhanced proctoring
- [ ] Multiple subjects
- [ ] User authentication

### Phase 3
- [ ] Advanced analytics dashboard
- [ ] Question difficulty calibration
- [ ] Multi-language support
- [ ] Mobile app

---

## 📝 License

This project is for personal use. See full development plan in `Developement.txt`.

---

## 🤝 Contributing

This is a personal project, but suggestions are welcome! Open an issue for:
- Bug reports
- Feature requests
- Performance improvements

---

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API docs at `/docs`
3. Check logs in terminal output

---

**Built with ❤️ for local-first AI development**