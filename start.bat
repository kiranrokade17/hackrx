@echo off
echo === LLM Query-Retrieval System - Quick Start ===
echo.

REM Check if virtual environment exists
if exist "venv\" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Run setup.ps1 first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found. Please create it with your API keys.
    echo You can copy .env.example to .env and edit it.
    pause
)

echo Starting the API server...
echo.
echo The API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python startup.py

pause
