# AI Interview Platform - Simple Setup Script for Windows
# This script sets up the local development environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Interview Platform - Local Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to project root
Set-Location E:\Projects\Saylo

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "OK Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}


# Check Ollama
Write-Host "`nChecking Ollama..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "OK Ollama found: $ollamaVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR Ollama not found" -ForegroundColor Red
    exit 1
}

# Create .env file
Write-Host "`nCreating .env file..." -ForegroundColor Yellow
if (Test-Path "backend\.env") {
    Write-Host "OK .env file already exists" -ForegroundColor Green
}
else {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "OK Created .env file" -ForegroundColor Green
}

# Update database password in .env
Write-Host "`nUpdating database password in .env..." -ForegroundColor Yellow
$envContent = Get-Content "backend\.env" -Raw
$envContent = $envContent -replace 'postgres:postgres', 'postgres:Admin@123'
Set-Content "backend\.env" -Value $envContent
Write-Host "OK Database password updated" -ForegroundColor Green

# Create virtual environment
Write-Host "`nCreating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "backend\venv") {
    Write-Host "OK Virtual environment already exists" -ForegroundColor Green
}
else {
    Set-Location backend
    python -m venv venv
    Set-Location ..
    Write-Host "OK Virtual environment created" -ForegroundColor Green
}

# Install dependencies
Write-Host "`nInstalling Python dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Cyan
Set-Location backend
& ".\venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
Set-Location ..
Write-Host "OK Dependencies installed" -ForegroundColor Green

# Create PostgreSQL database
Write-Host "`nSetting up PostgreSQL database..." -ForegroundColor Yellow
$env:PGPASSWORD = "Admin@123"
$dbCheck = psql -U postgres -lqt 2>&1 | Select-String -Pattern "saylo_interview"

if ($dbCheck) {
    Write-Host "OK Database 'saylo_interview' already exists" -ForegroundColor Green
}
else {
    $result = psql -U postgres -c "CREATE DATABASE saylo_interview;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK Database 'saylo_interview' created" -ForegroundColor Green
    }
    else {
        Write-Host "WARNING Could not create database automatically" -ForegroundColor Yellow
        Write-Host "Please create manually: psql -U postgres -c 'CREATE DATABASE saylo_interview;'" -ForegroundColor Yellow
    }
}

# Download Ollama models
Write-Host "`nDownloading Ollama models..." -ForegroundColor Yellow
Write-Host "This will take 5-10 minutes depending on your internet speed..." -ForegroundColor Cyan

Write-Host "`n  Downloading llama3.1:8b-instruct-q4_K_M..." -ForegroundColor Cyan
ollama pull llama3.1:8b-instruct-q4_K_M
Write-Host "  OK LLM model downloaded" -ForegroundColor Green

Write-Host "`n  Downloading nomic-embed-text..." -ForegroundColor Cyan
ollama pull nomic-embed-text
Write-Host "  OK Embedding model downloaded" -ForegroundColor Green

Write-Host "`n  Downloading llava:7b-q4 (optional, for proctoring)..." -ForegroundColor Cyan
$downloadVision = Read-Host "Download vision model? (y/n)"
if ($downloadVision -eq "y") {
    ollama pull llava:7b-q4
    Write-Host "  OK Vision model downloaded" -ForegroundColor Green
}
else {
    Write-Host "  SKIP Vision model skipped" -ForegroundColor Yellow
}

# Create data directories
Write-Host "`nCreating data directories..." -ForegroundColor Yellow
$directories = @("data\uploads", "data\chromadb", "data\recordings")

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  OK Created $dir" -ForegroundColor Green
    }
    else {
        Write-Host "  OK $dir already exists" -ForegroundColor Green
    }
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Start Ollama: ollama serve" -ForegroundColor White
Write-Host "2. Start backend: cd backend; .\venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "3. Start frontend: cd frontend; python -m http.server 8080" -ForegroundColor White
Write-Host "4. Open http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "Or use the start script: .\scripts\start_services.ps1" -ForegroundColor Cyan
Write-Host ""
