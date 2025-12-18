@echo off
REM Video Processing Pipeline Demo - Quick Start Script for Windows

echo Video Processing Pipeline Demo
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [+] Python found
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo [*] Creating virtual environment...
    python -m venv venv
    echo [+] Virtual environment created
)

REM Activate virtual environment
echo.
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo.
echo [*] Installing dependencies...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
echo [+] Dependencies installed

REM Run Streamlit app
echo.
echo [*] Starting Streamlit app...
echo    The app will open in your default browser.
echo    Press Ctrl+C to stop the server.
echo.
streamlit run app.py

pause

