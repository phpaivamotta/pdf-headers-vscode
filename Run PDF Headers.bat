@echo off
rem Double-click this file to open the PDF Header Tool.
rem The first time it runs it sets up Python packages automatically (needs internet, takes a minute).
cd /d "%~dp0"

".venv\Scripts\python.exe" -c "import pymupdf" >nul 2>&1
if errorlevel 1 (
    echo First-time setup: installing required packages. This only happens once...
    if exist ".venv" rmdir /s /q ".venv"
    python -m venv .venv
    if errorlevel 1 (
        echo.
        echo Python was not found. Install Python 3 from https://www.python.org/downloads/
        echo and tick "Add python.exe to PATH" during installation, then try again.
        pause
        exit /b 1
    )
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Package installation failed. Check your internet connection and try again.
        pause
        exit /b 1
    )
)

start "" ".venv\Scripts\pythonw.exe" main.py
