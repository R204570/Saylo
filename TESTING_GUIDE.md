# 🧪 TESTING & VALIDATION GUIDE
## Saylo AI Interview Platform

This guide helps you test and validate the MVP implementation.

---

## 📋 Pre-Testing Checklist

### System Requirements
- [ ] Python 3.11+ installed
- [ ] PostgreSQL 15+ installed and running
- [ ] Ollama installed and running
- [ ] At least 10GB free disk space
- [ ] Internet connection (for initial model downloads)

### Installation Verification
```powershell
# Check Python
python --version  # Should be 3.11+

# Check PostgreSQL
psql --version    # Should be 15+

# Check Ollama
ollama --version  # Should be latest

# Check if Ollama is running
ollama list       # Should show installed models
```

---

## 🚀 Step 1: Initial Setup

### Run Setup Script
```powershell
cd E:\Projects\Saylo
.\scripts\setup_local.ps1
```

**Expected Output**:
- ✓ Python found
- ✓ PostgreSQL found
- ✓ Ollama found
- ✓ Virtual environment created
- ✓ Dependencies installed
- ✓ Database created
- ✓ Models downloaded

### Verify Models
```powershell
ollama list
```

**Should show**:
- `llama3.1:8b-instruct-q4_K_M`
- `nomic-embed-text`
- `llava:7b-q4` (optional)

---

## 🧪 Step 2: Backend API Testing

### Start Backend
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

### Test 1: Health Check
```powershell
# In another terminal
curl http://localhost:8000/health
```

**Expected Response**:
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

✅ **PASS**: All services show "healthy"  
❌ **FAIL**: If Ollama shows "unhealthy", ensure `ollama serve` is running

### Test 2: API Documentation
Open browser: http://localhost:8000/docs

**Expected**: Swagger UI with all endpoints visible:
- `/health`
- `/api/sessions/*`
- `/api/upload/*`
- `/api/interview/*`

### Test 3: Upload Resume (via API)

Create a test resume file: `test_resume.txt`
```text
John Doe
Software Engineer

Skills:
- Python, JavaScript, React
- Machine Learning, AI
- PostgreSQL, MongoDB

Experience:
Senior Software Engineer at Tech Corp (2020-2024)
- Built scalable web applications
- Implemented ML models
```

Upload via curl:
```powershell
curl -X POST "http://localhost:8000/api/upload/resume" `
  -F "file=@test_resume.txt" `
  -F "session_id=test-001"
```

**Expected Response**:
```json
{
  "success": true,
  "file_path": "...",
  "parsed_data": {
    "skills": ["Python", "Javascript", "React", ...],
    "experience": [...],
    "education": []
  },
  "collection_name": "resume_test-001"
}
```

✅ **PASS**: File uploaded, skills extracted  
❌ **FAIL**: Check file path and permissions

### Test 4: Upload Reference Document

Create test reference: `test_reference.txt`
```text
Software Engineering Interview Guide

Common Topics:
1. Data Structures (Arrays, Trees, Graphs)
2. Algorithms (Sorting, Searching, Dynamic Programming)
3. System Design (Scalability, Databases, Caching)
4. Object-Oriented Programming
5. Web Technologies (REST APIs, HTTP, Authentication)
```

Upload:
```powershell
curl -X POST "http://localhost:8000/api/upload/reference" `
  -F "file=@test_reference.txt" `
  -F "session_id=test-001"
```

**Expected Response**:
```json
{
  "success": true,
  "file_path": "...",
  "chunk_count": 3,
  "collection_name": "reference_test-001"
}
```

✅ **PASS**: Document chunked and stored  
❌ **FAIL**: Check ChromaDB connection

### Test 5: Create Session

```powershell
curl -X POST "http://localhost:8000/api/sessions/create" `
  -H "Content-Type: application/json" `
  -d '{
    "subject_name": "Software Engineer Interview",
    "resume_path": "test_resume.txt",
    "reference_doc_path": "test_reference.txt"
  }'
```

**Expected Response**:
```json
{
  "session_id": "uuid-here",
  "subject_name": "Software Engineer Interview",
  "started_at": "2026-01-22T...",
  "status": "SCHEDULED"
}
```

**Save the session_id for next tests!**

### Test 6: Start Session

```powershell
# Replace {session_id} with actual ID
curl -X POST "http://localhost:8000/api/sessions/{session_id}/start"
```

**Expected Response**:
```json
{
  "session_id": "...",
  "livekit_room_id": "room_...",
  "status": "IN_PROGRESS"
}
```

### Test 7: Generate Question

```powershell
curl -X POST "http://localhost:8000/api/interview/generate-question" `
  -H "Content-Type: application/json" `
  -d '{
    "session_id": "your-session-id",
    "question_number": 1
  }'
```

**Expected Response**:
```json
{
  "question_id": "...",
  "question_text": "Can you explain your experience with Python and how you've used it in production?",
  "question_order": 1
}
```

✅ **PASS**: Question is relevant to resume  
❌ **FAIL**: Check Ollama connection and context retrieval

**Save the question_id for next test!**

### Test 8: Submit Answer

```powershell
curl -X POST "http://localhost:8000/api/interview/submit-answer" `
  -H "Content-Type: application/json" `
  -d '{
    "session_id": "your-session-id",
    "question_id": "your-question-id",
    "answer_text": "I have 4 years of experience with Python. I built ML models using scikit-learn and deployed them with FastAPI. I also created data pipelines with Pandas and automated tasks with Python scripts."
  }'
```

**Expected Response**:
```json
{
  "question_id": "...",
  "evaluation": {
    "correctness_score": 8,
    "completeness_score": 7,
    "clarity_score": 8,
    "overall_score": 7.7,
    "feedback": "Good answer with specific examples...",
    "strengths": ["Mentioned specific libraries", "Real-world examples"],
    "improvements": ["Could elaborate on challenges faced"]
  }
}
```

✅ **PASS**: Answer evaluated with scores and feedback  
❌ **FAIL**: Check LLM response parsing

### Test 9: Get Transcript

```powershell
curl "http://localhost:8000/api/interview/{session_id}/transcript"
```

**Expected**: Array of transcript entries

### Test 10: End Session

```powershell
curl -X POST "http://localhost:8000/api/sessions/{session_id}/end"
```

**Expected Response**:
```json
{
  "session_id": "...",
  "status": "COMPLETED",
  "duration_seconds": 120
}
```

---

## 🎨 Step 3: Frontend Testing

### Start Frontend
```powershell
cd frontend
python -m http.server 8080
```

### Open Browser
Navigate to: http://localhost:8080

### Test 1: Page Load
✅ **PASS**: Page loads with gradient background, no console errors  
❌ **FAIL**: Check browser console for errors

### Test 2: Upload Resume
1. Click "Choose File" for resume
2. Select test_resume.txt
3. Click "Upload Resume"

**Expected**: Green success message with extracted skills

### Test 3: Upload Reference
1. Click "Choose File" for reference
2. Select test_reference.txt
3. Click "Upload Reference"

**Expected**: Green success message with chunk count

### Test 4: Create Session
1. Enter subject name: "Software Engineer Interview"
2. Click "Create Session"

**Expected**: 
- Success message with session ID
- Interview section appears

### Test 5: Start Interview
1. Click "Start Interview"

**Expected**:
- Question appears in purple box
- Answer textarea visible
- Question is relevant to resume

### Test 6: Submit Answer
1. Type answer in textarea
2. Click "Submit Answer"

**Expected**:
- Evaluation results appear
- Scores displayed (0-10)
- Feedback shown
- Prompt for next question

### Test 7: Complete Interview
1. Answer all 8 questions
2. Session ends automatically

**Expected**:
- Analytics section appears
- Transcript displayed
- All Q&A pairs shown

---

## 🔍 Step 4: Database Verification

### Connect to PostgreSQL
```powershell
psql -U postgres -d saylo_interview
```

### Check Tables
```sql
\dt
```

**Expected Tables**:
- interview_sessions
- questions
- session_transcripts
- session_analytics
- proctoring_events

### Check Session Data
```sql
SELECT * FROM interview_sessions;
```

**Expected**: Your test session with status "COMPLETED"

### Check Questions
```sql
SELECT question_text FROM questions WHERE session_id = 'your-session-id';
```

**Expected**: 8 questions

### Check Transcripts
```sql
SELECT speaker, text_content FROM session_transcripts WHERE session_id = 'your-session-id';
```

**Expected**: Transcript entries

---

## 📊 Step 5: ChromaDB Verification

### Check Collections (via Python)
```python
cd backend
.\venv\Scripts\Activate.ps1
python

>>> import chromadb
>>> client = chromadb.PersistentClient(path="../data/chromadb")
>>> collections = client.list_collections()
>>> print([c.name for c in collections])
```

**Expected**: 
- `resume_test-001`
- `reference_test-001`

### Query Collection
```python
>>> collection = client.get_collection("resume_test-001")
>>> results = collection.query(query_texts=["Python skills"], n_results=2)
>>> print(results['documents'])
```

**Expected**: Relevant resume chunks

---

## ⚡ Step 6: Performance Testing

### Test 1: Question Generation Speed
```powershell
# Time the request
Measure-Command {
  curl -X POST "http://localhost:8000/api/interview/generate-question" `
    -H "Content-Type: application/json" `
    -d '{"session_id": "test-001", "question_number": 1}'
}
```

**Expected**: 3-5 seconds  
⚠️ **Warning**: >10 seconds indicates performance issue

### Test 2: Answer Evaluation Speed
```powershell
Measure-Command {
  curl -X POST "http://localhost:8000/api/interview/submit-answer" `
    -H "Content-Type: application/json" `
    -d '{"session_id": "...", "question_id": "...", "answer_text": "Test answer"}'
}
```

**Expected**: 5-8 seconds

### Test 3: VRAM Usage
```powershell
nvidia-smi
```

**Expected**: 
- GPU Memory Used: ~3-3.5GB
- GPU Utilization: 50-80% during inference

⚠️ **Warning**: >3.8GB indicates VRAM issue

---

## 🐛 Common Issues & Solutions

### Issue 1: Ollama Not Responding
```powershell
# Check if running
ollama list

# Restart
taskkill /F /IM ollama.exe
ollama serve
```

### Issue 2: Database Connection Error
```powershell
# Check service
Get-Service postgresql*

# Restart
Restart-Service postgresql-x64-15
```

### Issue 3: Import Errors
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install --force-reinstall -r requirements.txt
```

### Issue 4: ChromaDB Errors
```powershell
# Delete and recreate
Remove-Item -Recurse -Force data\chromadb
mkdir data\chromadb
```

### Issue 5: VRAM Out of Memory
Edit `backend/.env`:
```env
VISION_ENABLED=false
MAX_CONTEXT_TOKENS=1500
```

---

## ✅ Success Criteria

### MVP is successful if:
- [x] All backend API tests pass
- [x] Frontend loads and functions
- [x] Resume parsing extracts skills
- [x] Questions are contextually relevant
- [x] Answers are evaluated with feedback
- [x] Database stores all data
- [x] ChromaDB retrieves context
- [x] Performance is acceptable (<10s per operation)
- [x] VRAM stays under 3.8GB

---

## 📈 Next Steps After Testing

### If All Tests Pass:
1. ✅ Test with real resume and documents
2. ✅ Try different subjects/roles
3. ✅ Experiment with settings
4. ✅ Review generated questions quality
5. ✅ Optimize performance if needed

### If Tests Fail:
1. Check logs in terminal
2. Review error messages
3. Consult troubleshooting section
4. Check IMPLEMENTATION_SUMMARY.md
5. Verify all dependencies installed

---

## 🎯 Performance Benchmarks

### Target Metrics (on i5 11th Gen, RTX 3050):
| Operation | Target | Acceptable | Poor |
|-----------|--------|------------|------|
| Question Gen | <5s | <10s | >10s |
| Answer Eval | <8s | <15s | >15s |
| File Upload | <3s | <5s | >5s |
| Page Load | <2s | <5s | >5s |
| VRAM Usage | <3.5GB | <3.8GB | >3.8GB |

---

## 📝 Test Report Template

```markdown
# Test Report - Saylo MVP

**Date**: 
**Tester**: 
**Hardware**: i5 11th Gen, 32GB RAM, RTX 3050 4GB

## Results

### Backend API
- [ ] Health check: PASS/FAIL
- [ ] Resume upload: PASS/FAIL
- [ ] Reference upload: PASS/FAIL
- [ ] Session creation: PASS/FAIL
- [ ] Question generation: PASS/FAIL
- [ ] Answer evaluation: PASS/FAIL

### Frontend
- [ ] Page load: PASS/FAIL
- [ ] File upload UI: PASS/FAIL
- [ ] Interview flow: PASS/FAIL
- [ ] Analytics display: PASS/FAIL

### Performance
- Question gen time: ___s
- Answer eval time: ___s
- VRAM usage: ___GB

### Issues Found
1. 
2. 

### Overall Status
- [ ] Ready for use
- [ ] Needs fixes
- [ ] Major issues
```

---

**Happy Testing! 🧪**
