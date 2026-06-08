# AI PC Troubleshooting Agent Launcher (PowerShell)
# Run: powershell -ExecutionPolicy Bypass -File "launch.ps1"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AI PC Troubleshooting Agent" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "  Install Python 3.8+ from https://www.python.org" -ForegroundColor Yellow
    Write-Host "  Check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green

# Check if pip is available
pip --version 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] pip is not available" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] pip found" -ForegroundColor Green

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
        Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[OK] All dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "[*] Launching AI PC Troubleshooting Agent..." -ForegroundColor Cyan
Write-Host ""

# Launch the application
python main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Application failed to start" -ForegroundColor Red
    Write-Host "  Check the error message above" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
