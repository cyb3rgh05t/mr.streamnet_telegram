# Quick Setup Script for Telegram Bot Web UI

Write-Host "🤖 Telegram Bot Web UI - Setup Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Found Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found! Please install Node.js 20+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 1: Setting up Python environment..." -ForegroundColor Cyan

# Create virtual environment if it doesn't exist
if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✓ Python dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Setting up Frontend..." -ForegroundColor Cyan

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green

# Build frontend
Write-Host "Building frontend for production..." -ForegroundColor Yellow
npm run build
Write-Host "✓ Frontend built successfully" -ForegroundColor Green
Set-Location ..

Write-Host ""
Write-Host "Step 3: Configuration..." -ForegroundColor Cyan

# Check if config.json exists
if (!(Test-Path "config\config.json")) {
    Write-Host "Creating config.json from example..." -ForegroundColor Yellow
    Copy-Item "config\config.json.example" "config\config.json"
    Write-Host "✓ Config file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Please edit config\config.json with your settings!" -ForegroundColor Yellow
    Write-Host "   - Add your Telegram bot token" -ForegroundColor Yellow
    Write-Host "   - Add your Sonarr/Radarr API keys" -ForegroundColor Yellow
    Write-Host "   - Add your TMDB API key" -ForegroundColor Yellow
} else {
    Write-Host "✓ Config file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit config\config.json with your API keys and settings" -ForegroundColor White
Write-Host "2. Run: python bot.py" -ForegroundColor White
Write-Host "3. Access Web UI at: http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "For development:" -ForegroundColor Cyan
Write-Host "- Backend API: cd api && uvicorn main:app --reload" -ForegroundColor White
Write-Host "- Frontend dev: cd frontend && npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Need help? Check WEB_UI_README.md" -ForegroundColor Yellow
Write-Host ""
