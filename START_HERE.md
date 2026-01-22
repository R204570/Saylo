# 🚀 SIMPLE STARTUP GUIDE

## Current Status
✅ Python dependencies installing...

## What to Do Next (In Order)

### 1. Wait for Dependencies to Finish Installing
The `pip install` command is running. Wait for it to complete (2-3 minutes).

### 2. Create Database (1 minute)
```powershell
cd E:\Projects\Saylo\backend
.\venv\Scripts\Activate.ps1
python create_database.py
```

This script will:
- Connect to PostgreSQL
- Create `saylo_interview` database
- Test the connection

### 3. Download Ollama Models (5-10 minutes)
```powershell
# In a NEW terminal
ollama pull llama3.1:8b-instruct-q4_K_M
ollama pull nomic-embed-text
```

### 4. Start Ollama Server
```powershell
# Keep this terminal open
ollama serve
```

### 5. Start Backend API
```powershell
# In a NEW terminal
cd E:\Projects\Saylo\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 6. Start Frontend
```powershell
# In a NEW terminal
cd E:\Projects\Saylo\frontend
python -m http.server 8080
```

### 7. Open Browser
Go to: **http://localhost:8080**

---

## Quick Test

### Test Backend Health
Open: **http://localhost:8000/health**

Should show:
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

### Test API Docs
Open: **http://localhost:8000/docs**

You'll see interactive API documentation.

---

## Your First Interview

1. **Upload Resume**
   - Create a text file: `my_resume.txt`
   - Add your skills, experience
   - Upload via web interface

2. **Upload Reference**
   - Create: `interview_topics.txt`
   - Add interview topics/questions
   - Upload via web interface

3. **Create Session**
   - Subject: "Software Engineer Interview"
   - Click "Create Session"

4. **Start Interview**
   - Click "Start Interview"
   - Answer AI-generated questions
   - Get instant feedback!

---

## Troubleshooting

### "Database connection error"
Run the database creation script:
```powershell
cd E:\Projects\Saylo\backend
.\venv\Scripts\Activate.ps1
python create_database.py
```

### "Ollama not responding"
Make sure Ollama is running:
```powershell
ollama serve
```

### "Port already in use"
Kill the process:
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## Notes

- **Redis**: Not required for MVP, it's optional
- **LiveKit**: For future voice features, not needed yet
- **Vision Model**: Optional, for proctoring

---

**You're almost there! Just follow the steps above in order.** 🎯
