@echo off
REM AI PC Troubleshooting Agent Launcher
REM This script installs dependencies and runs the application

echo.
echo ============================================
echo  AI PC Troubleshooting Agent
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [*] Python found
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not available
    pause
    exit /b 1
)

echo [*] pip found
echo.

REM Check if requirements are installed
echo [*] Checking dependencies...
pip show customtkinter >nul 2>&1
if errorlevel 1 (
    echo [!] Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo [*] Dependencies already installed
)

echo.
echo [*] Launching AI PC Troubleshooting Agent...
echo.

REM Run the application
python main.py

if errorlevel 1 (
    echo.
    echo Error: Application failed to start
    echo Please check the error message above
    pause
)
