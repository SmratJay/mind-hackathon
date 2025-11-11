# Launch script for the GUI simulator
# No external dependencies needed!

Write-Host "🚀 Launching 4-Bit Processor Simulator GUI..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starting simulator..." -ForegroundColor Yellow
Write-Host ""

# Launch the GUI
python simulator_gui.py
