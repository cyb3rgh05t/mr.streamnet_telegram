# Development Scripts

Write-Host "🤖 Telegram Bot - Development Menu" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start Bot (Production)" -ForegroundColor Green
Write-Host "2. Start Backend API (Development)" -ForegroundColor Yellow
Write-Host "3. Start Frontend (Development)" -ForegroundColor Yellow
Write-Host "4. Build Frontend" -ForegroundColor Blue
Write-Host "5. Run All (Bot + Web UI)" -ForegroundColor Magenta
Write-Host "6. Exit" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "Select an option (1-6)"

switch ($choice) {
    "1" {
        Write-Host "`nStarting bot..." -ForegroundColor Green
        & .venv\Scripts\Activate.ps1
        python bot.py
    }
    "2" {
        Write-Host "`nStarting Backend API (http://localhost:5000)..." -ForegroundColor Yellow
        & .venv\Scripts\Activate.ps1
        Set-Location api
        uvicorn main:app --reload --port 5000
    }
    "3" {
        Write-Host "`nStarting Frontend Dev Server (http://localhost:5173)..." -ForegroundColor Yellow
        Set-Location frontend
        npm run dev
    }
    "4" {
        Write-Host "`nBuilding frontend..." -ForegroundColor Blue
        Set-Location frontend
        npm run build
        Write-Host "`n✓ Build complete! Output in frontend/dist" -ForegroundColor Green
    }
    "5" {
        Write-Host "`nStarting Bot with Web UI..." -ForegroundColor Magenta
        Write-Host "Make sure config.json has 'WEB_ENABLED': true" -ForegroundColor Yellow
        & .venv\Scripts\Activate.ps1
        python bot.py
    }
    "6" {
        Write-Host "`nGoodbye! 👋" -ForegroundColor Cyan
        exit
    }
    default {
        Write-Host "`nInvalid option!" -ForegroundColor Red
    }
}
