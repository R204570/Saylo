# 🚀 QUICK START GUIDE - Saylo AI Interview Platform

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.11+
- ✅ PostgreSQL 15+
- ✅ Ollama installed
- ✅ Git (for version control)

## Step-by-Step Setup (Windows)

### 1. Install Ollama
```powershell
# Download from https://ollama.ai/download
# Or use winget
winget install Ollama.Ollama
```

### 2. Install PostgreSQL
```powershell
# Download from https://www.postgresql.org/download/windows/
# Or use chocolatey
choco install postgresql
```

### 3. Run Setup Script
```powershell
# Navigate to project directory
cd E:\Projects\Saylo

# Run setup script
.\scripts\setup_local.ps1
```

The script will:
- ✅ Check dependencies
- ✅ Create virtual environment
- ✅ Install Python packages
- ✅ Create PostgreSQL database
- ✅ Download AI models
- ✅ Create data directories

### 4. Start Services

#### Option A: Manual Start (Recommended for first time)

```powershell
# Terminal 1: Start Ollama (if not running as service)
ollama serve

# Terminal 2: Start PostgreSQL (usually runs as service)
# Check: Services → PostgreSQL

# Terminal 3: Start Backend
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 4: Start Frontend
cd frontend
python -m http.server 8080
```

#### Option B: Using Docker Compose (for PostgreSQL & Redis)

```powershell
# Start database services
docker-compose up -d

# Then start backend and frontend as above
```

### 5. Verify Installation

Open your browser and check:
- Frontend: http://localhost:8080
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "services": {
    "ollama": "healthy",
    "database": "healthy",
    "api": "healthy"
  }
}
```

## First Interview Session

### 1. Upload Files
- Click "Upload Resume" and select your resume (PDF/DOCX)
- Click "Upload Reference" and select interview guide/study material

### 2. Create Session
- Enter subject name (e.g., "Software Engineer Interview")
- Click "Create Session"

### 3. Start Interview
- Click "Start Interview"
- AI will generate first question based on your resume and reference material
- Type your answer in the text box
- Click "Submit Answer" to get evaluation
- Continue for 8 questions

### 4. View Analytics
- After completing all questions, session ends automatically
- View transcript, questions, answers, and response times

## Troubleshooting

### Ollama Not Responding
```powershell
# Check if Ollama is running
ollama list

# If not, start it
ollama serve

# Verify models are downloaded
ollama list
# Should show: llama3.1:8b-instruct-q4_K_M, nomic-embed-text
```

### Database Connection Error
```powershell
# Check PostgreSQL service
Get-Service postgresql*

# If not running, start it
Start-Service postgresql-x64-15

# Test connection
psql -U postgres -d saylo_interview
```

### Backend Import Errors
```powershell
# Reinstall dependencies
cd backend
.\venv\Scripts\Activate.ps1
pip install --force-reinstall -r requirements.txt
```

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

## Performance Tips

### VRAM Management
- Monitor GPU usage: `nvidia-smi`
- If VRAM issues, disable vision: Set `VISION_ENABLED=false` in `.env`
- Use smaller context: Reduce `MAX_CONTEXT_TOKENS` in `.env`

### Speed Optimization
- Pre-load models: Run `ollama pull` for all models before starting
- Use SSD for ChromaDB storage
- Increase `chunk_size` if processing is slow

## Next Steps

Once MVP is working:
1. ✅ Test with different resumes and reference documents
2. ✅ Experiment with different subjects
3. ✅ Review generated questions and evaluations
4. ✅ Check analytics and transcripts
5. ✅ Optimize performance based on your hardware

## Advanced Configuration

Edit `backend/.env` for customization:

```env
# Increase context for better questions
MAX_CONTEXT_TOKENS=3000

# More questions per session
QUESTION_COUNT=10

# Enable/disable proctoring
VISION_ENABLED=true
VISION_FRAME_INTERVAL=5

# Adjust chunk size for documents
CHUNK_SIZE=500
CHUNK_OVERLAP=100
```

## Getting Help

1. Check logs in terminal output
2. Visit API docs: http://localhost:8000/docs
3. Review `LOCAL_MVP_PLAN.md` for architecture details
4. Check `Developement.txt` for full development plan

## Success Checklist

- [ ] Ollama running and models downloaded
- [ ] PostgreSQL database created
- [ ] Backend API responding (health check passes)
- [ ] Frontend accessible
- [ ] Resume uploaded successfully
- [ ] Reference document uploaded successfully
- [ ] Session created
- [ ] First question generated
- [ ] Answer evaluated
- [ ] Analytics displayed

If all checked, you're ready to go! 🎉

---

**Happy Interviewing! 🚀**
