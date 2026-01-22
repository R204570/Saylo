# 🚀 MANUAL SETUP GUIDE - Step by Step

Since you have PostgreSQL 18, Docker, and Ollama already installed, let's set up manually.

## Step 1: Add PostgreSQL to PATH (One-time)

PostgreSQL is installed but not in your system PATH. Let's fix that:

1. Find your PostgreSQL bin directory (usually):
   - `C:\Program Files\PostgreSQL\18\bin`

2. Add to PATH:
   ```powershell
   # Run this in PowerShell as Administrator
   $pgPath = "C:\Program Files\PostgreSQL\18\bin"
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$pgPath", "Machine")
   ```

3. **Restart your terminal** after adding to PATH

4. Verify:
   ```powershell
   psql --version
   ```

## Step 2: Create Python Virtual Environment

```powershell
cd E:\Projects\Saylo\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## Step 3: Install Python Dependencies

```powershell
# Make sure you're in backend folder with venv activated
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- FastAPI
- SQLAlchemy
- ChromaDB
- Ollama client
- And all other dependencies

**Time**: 2-3 minutes

## Step 4: Create .env File

```powershell
cd E:\Projects\Saylo\backend
copy .env.example .env
```

The .env file is already configured with your PostgreSQL password (Admin@123).

## Step 5: Create PostgreSQL Database

```powershell
# Set password environment variable
$env:PGPASSWORD = "Admin@123"

# Create database
psql -U postgres -c "CREATE DATABASE saylo_interview;"

# Verify
psql -U postgres -l
```

You should see `saylo_interview` in the list.

## Step 6: Download Ollama Models

```powershell
# Start Ollama if not running
ollama serve

# In another terminal, download models:
ollama pull llama3.1:8b-instruct-q4_K_M
ollama pull nomic-embed-text

# Optional (for proctoring):
ollama pull llava:7b-q4
```

**Time**: 5-10 minutes depending on internet speed

**Sizes**:
- llama3.1:8b-instruct-q4_K_M: ~4.5GB
- nomic-embed-text: ~300MB
- llava:7b-q4: ~4GB (optional)

## Step 7: Verify Ollama Models

```powershell
ollama list
```

You should see:
```
NAME                              SIZE
llama3.1:8b-instruct-q4_K_M      4.5 GB
nomic-embed-text                 274 MB
llava:7b-q4                      4.0 GB (if downloaded)
```

## Step 8: Create Data Directories

```powershell
cd E:\Projects\Saylo
mkdir data\uploads -Force
mkdir data\chromadb -Force
mkdir data\recordings -Force
```

## Step 9: Test Backend

```powershell
cd E:\Projects\Saylo\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

Open browser: http://localhost:8000/health

**Expected response**:
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

## Step 10: Test Frontend

Open **NEW terminal**:
```powershell
cd E:\Projects\Saylo\frontend
python -m http.server 8080
```

Open browser: http://localhost:8080

You should see the Saylo interface!

---

## 🎯 Quick Start Commands (After Setup)

### Terminal 1: Ollama
```powershell
ollama serve
```

### Terminal 2: Backend
```powershell
cd E:\Projects\Saylo\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

### Terminal 3: Frontend
```powershell
cd E:\Projects\Saylo\frontend
python -m http.server 8080
```

Then open: http://localhost:8080

---

## 🐛 Troubleshooting

### Issue: "psql is not recognized"
**Solution**: Add PostgreSQL to PATH (see Step 1)

### Issue: "Ollama not responding"
**Solution**: 
```powershell
# Check if running
ollama list

# Start if not running
ollama serve
```

### Issue: "Database connection error"
**Solution**:
```powershell
# Check PostgreSQL service
Get-Service postgresql*

# Start if needed
Start-Service postgresql-x64-18
```

### Issue: "Import errors in Python"
**Solution**:
```powershell
cd E:\Projects\Saylo\backend
.\venv\Scripts\Activate.ps1
pip install --force-reinstall -r requirements.txt
```

### Issue: "Port 8000 already in use"
**Solution**:
```powershell
# Find process
netstat -ano | findstr :8000

# Kill it (replace PID)
taskkill /PID <PID> /F
```

---

## ✅ Verification Checklist

- [ ] PostgreSQL in PATH (`psql --version` works)
- [ ] Python venv created in `backend/venv`
- [ ] Dependencies installed (no errors)
- [ ] .env file exists in `backend/`
- [ ] Database `saylo_interview` created
- [ ] Ollama models downloaded
- [ ] Backend starts without errors
- [ ] Health check returns healthy
- [ ] Frontend loads in browser

---

## 🎉 You're Ready!

Once all steps are complete, you can:
1. Upload a resume
2. Upload a reference document
3. Create an interview session
4. Start practicing!

---

**Need help? Check the error messages and refer to the troubleshooting section above.**
