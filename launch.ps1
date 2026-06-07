# AI PC Troubleshooting Agent Launcher (PowerShell)
# Run this script with: powershell -ExecutionPolicy Bypass -File "launch.ps1"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AI PC Troubleshooting Agent" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "    Please install Python 3.8+ from https://www.python.org" -ForegroundColor Yellow
    Write-Host "    Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if pip is available
try {
    $pipVersion = pip --version 2>&1
    Write-Host "[✓] pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] Error: pip is not available" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[*] Checking dependencies..." -ForegroundColor Yellow

# Check and install requirements
$packagesNeeded = @()
$requiredPackages = @("customtkinter", "psutil", "wmi")

foreach ($package in $requiredPackages) {
    $installed = pip show $package 2>&1 | Select-String "Name:"
    if (-not $installed) {
        $packagesNeeded += $package
    }
}

if ($packagesNeeded.Count -gt 0) {
    Write-Host "[!] Installing required packages..." -ForegroundColor Yellow
    Write-Host "    Packages: $($packagesNeeded -join ', ')" -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[✗] Error: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[✓] All dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "[*] Launching AI PC Troubleshooting Agent..." -ForegroundColor Cyan
Write-Host ""

# Launch the application
python main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[✗] Error: Application failed to start" -ForegroundColor Red
    Write-Host "    Please check the error message above" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
