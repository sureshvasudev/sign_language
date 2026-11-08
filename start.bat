@echo off
REM ============================================================
REM  AI Sign Language Translator - one-click start
REM  Double-click this file (or run "start.bat" in a command prompt).
REM  It sets up Python the first time, starts the server,
REM  and opens the app in the browser when the server is ready.
REM  To stop the app: close this window, or press Ctrl+C in it.
REM ============================================================

REM When the script calls itself with "open-browser", jump to that part.
if "%~1"=="open-browser" goto open_browser

title AI Sign Language Translator
REM Work from the folder this script lives in, wherever it was started from.
cd /d "%~dp0"

REM Step 1: first-time setup - create the Python environment and install libraries.
if not exist ".venv\Scripts\python.exe" (
    echo First-time setup: creating the Python environment. This can take several minutes...
    where python >nul 2>nul
    if errorlevel 1 (
        echo.
        echo ERROR: Python was not found. Install Python 3.10 or newer from python.org
        echo and tick "Add Python to PATH" during install. Then run this script again.
        pause
        exit /b 1
    )
    python -m venv .venv
    ".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Installing the libraries failed. Check the internet connection and try again.
        rmdir /s /q .venv
        pause
        exit /b 1
    )
)

REM Step 2: in the background, wait for the server and then open the browser.
start "" /b cmd /c ""%~f0" open-browser"

REM Step 3: start the server. This window must stay open while the app is used.
echo.
echo Starting the server. The browser will open by itself when it is ready.
echo Keep this window open. Close it (or press Ctrl+C) to stop the app.
echo.
".venv\Scripts\python.exe" -m uvicorn backend.app:app --port 8000
echo.
echo The server has stopped.
pause
exit /b 0

REM Waits until http://localhost:8000 answers, then opens it in the default browser.
:open_browser
ping -n 3 127.0.0.1 >nul
curl -s -o nul http://localhost:8000
if errorlevel 1 goto open_browser
start "" http://localhost:8000
exit /b 0
