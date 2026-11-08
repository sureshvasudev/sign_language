@echo off
REM ============================================================
REM  AI Sign Language Translator - reset the statistics to 0
REM  Double-click this file (or run "reset.bat" in a command prompt).
REM  The old numbers are not deleted: each reset saves them in its
REM  own dated file in backend\stats-backups\, so you can always
REM  see what was there before.
REM ============================================================

title Reset statistics
REM Work from the folder this script lives in, wherever it was started from.
cd /d "%~dp0"

REM If there is no statistics file, the counters are already 0.
if not exist "backend\stats.json" (
    echo The statistics are already at 0. Nothing to reset.
    pause
    exit /b 0
)

REM Show the current numbers, so you know what is about to be reset.
echo These are the statistics now, one entry per day:
echo.
type "backend\stats.json"
echo.
echo.

REM Ask before resetting, so it cannot happen by accident.
set /p ANSWER=Reset all statistics to 0? Type Y and press Enter:
if /i not "%ANSWER%"=="Y" (
    echo Cancelled. Nothing was changed.
    pause
    exit /b 0
)

REM Get the date and time, for example 2026-11-08_14-30-05, to name the backup file.
for /f %%t in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set STAMP=%%t
set BACKUP=backend\stats-backups\stats-%STAMP%.json

REM Move the old numbers into the backup folder (it is made the first time).
if not exist "backend\stats-backups" mkdir "backend\stats-backups"
move "backend\stats.json" "%BACKUP%" >nul
if errorlevel 1 (
    echo ERROR: Could not reset the statistics. Close any program that has stats.json open and try again.
    pause
    exit /b 1
)

echo Done. All statistics are now 0.
echo The old numbers are saved in %BACKUP%
echo If the app is open in the browser, refresh the page to see the zeros.
pause
exit /b 0
