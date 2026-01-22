# Saylo AI Interview Platform - Start All Services
# This script starts all required services for the platform

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Saylo AI Interview Platform" -ForegroundColor Cyan
Write-Host "Starting All Services..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if setup has been run
if (!(Test-Path "backend\.env")) {
    Write-Host "⚠️  Setup not completed. Running setup first..." -ForegroundColor Yellow
    .\scripts\setup_local.ps1
    Write-Host ""
}

# Function to check if a port is in use
function Test-Port {
    param($Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    return $connection
}

# Check Ollama
Write-Host "Checking Ollama..." -ForegroundColor Yellow
try {
    $ollamaRunning = Test-Port 11434
    if ($ollamaRunning) {
        Write-Host "✓ Ollama is already running" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Ollama is not running. Please start it manually:" -ForegroundColor Yellow
        Write-Host "   Open a new terminal and run: ollama serve" -ForegroundColor White
        Write-Host ""
        $response = Read-Host "Press Enter when Ollama is running, or 'q' to quit"
        if ($response -eq 'q') { exit }
    }
}
catch {
    Write-Host "⚠️  Cannot check Ollama status" -ForegroundColor Yellow
}

# Check PostgreSQL
Write-Host "`nChecking PostgreSQL..." -ForegroundColor Yellow
try {
    $pgRunning = Test-Port 5432
    if ($pgRunning) {
        Write-Host "✓ PostgreSQL is running" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  PostgreSQL is not running. Starting service..." -ForegroundColor Yellow
        Start-Service postgresql* -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Write-Host "✓ PostgreSQL started" -ForegroundColor Green
    }
}
catch {
    Write-Host "⚠️  Cannot start PostgreSQL. Please start it manually" -ForegroundColor Yellow
}

# Start Docker services (optional)
Write-Host "`nDocker services (PostgreSQL, Redis, LiveKit)..." -ForegroundColor Yellow
$useDocker = Read-Host "Start Docker services? (y/n)"
if ($useDocker -eq 'y') {
    Write-Host "Starting Docker Compose..." -ForegroundColor Cyan
    docker-compose up -d
    Write-Host "✓ Docker services started" -ForegroundColor Green
    Start-Sleep -Seconds 3
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Starting Application Services..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Start Backend
Write-Host "`nStarting Backend API..." -ForegroundColor Yellow
Write-Host "This will open a new terminal window" -ForegroundColor White

$backendScript = @"
cd backend
.\venv\Scripts\Activate.ps1
Write-Host '========================================' -ForegroundColor Green
Write-Host 'Backend API Server' -ForegroundColor Green
Write-Host '========================================' -ForegroundColor Green
Write-Host 'API: http://localhost:8000' -ForegroundColor Cyan
Write-Host 'Docs: http://localhost:8000/docs' -ForegroundColor Cyan
Write-Host 'Health: http://localhost:8000/health' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Green
Write-Host ''
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "`nStarting Frontend..." -ForegroundColor Yellow
Write-Host "This will open a new terminal window" -ForegroundColor White

$frontendScript = @"
cd frontend
Write-Host '========================================' -ForegroundColor Green
Write-Host 'Frontend Server' -ForegroundColor Green
Write-Host '========================================' -ForegroundColor Green
Write-Host 'URL: http://localhost:8080' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Green
Write-Host ''
python -m http.server 8080
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Start-Sleep -Seconds 2

# Summary
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "All Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Yellow
Write-Host "  Frontend:    http://localhost:8080" -ForegroundColor Cyan
Write-Host "  API:         http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Health:      http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:8080 in your browser" -ForegroundColor White
Write-Host "2. Upload your resume and reference document" -ForegroundColor White
Write-Host "3. Create an interview session" -ForegroundColor White
Write-Host "4. Start practicing!" -ForegroundColor White
Write-Host ""
Write-Host "To stop services:" -ForegroundColor Yellow
Write-Host "  - Close the terminal windows" -ForegroundColor White
Write-Host "  - Or press Ctrl+C in each terminal" -ForegroundColor White
Write-Host ""
Write-Host "For help, see QUICKSTART.md" -ForegroundColor Cyan
Write-Host ""

# Open browser
$openBrowser = Read-Host "Open browser now? (y/n)"
if ($openBrowser -eq 'y') {
    Start-Process "http://localhost:8080"
}

Write-Host "`nPress any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
