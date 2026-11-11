@echo off
REM ============================================================
REM  Copy the project to the AWS server and set it up there.
REM  Run it once after creating the stack, and again after any code change.
REM  It does not touch the statistics already on the server.
REM  Needs: deploy\signlang-key.pem (see STEPS.md) and DuckDNS pointing at the server.
REM ============================================================

REM The server's address. Change this if your DuckDNS name changes.
set SERVER=mysignlang.duckdns.org
set KEY=deploy\signlang-key.pem

title Upload to AWS
REM Work from the project folder (one level above this script).
cd /d "%~dp0.."

if not exist "%KEY%" (
    echo ERROR: %KEY% not found. See step 5 of deploy\STEPS.md.
    pause
    exit /b 1
)

REM SSH refuses a key that other Windows users can read, so let only you read it.
icacls "%KEY%" /inheritance:r /grant:r "%USERNAME%:R" >nul

REM Pack the app into one file. Leave out the laptop's Python, statistics, debug pictures and the key.
echo Packing the project...
tar -czf "%TEMP%\signlang.tgz" --exclude=__pycache__ --exclude=debug --exclude=stats.json --exclude=stats-backup.json --exclude=stats-backups --exclude=*.pem --exclude=*.tmp backend frontend test_photos deploy
if errorlevel 1 (
    echo ERROR: Could not pack the project.
    pause
    exit /b 1
)

REM Copy it to the server, unpack it, and run the setup script there.
echo Copying to %SERVER%...
scp -i "%KEY%" -o StrictHostKeyChecking=accept-new "%TEMP%\signlang.tgz" ubuntu@%SERVER%:signlang.tgz
if errorlevel 1 (
    echo ERROR: Could not copy to the server. Check that DuckDNS shows the server's IP, and that your home IP has not changed.
    pause
    exit /b 1
)
echo Setting up the server. The first time this takes about 10 minutes...
ssh -i "%KEY%" ubuntu@%SERVER% "mkdir -p sign_language && tar -xzf signlang.tgz -C sign_language && bash sign_language/deploy/setup.sh %SERVER%"
if errorlevel 1 (
    echo ERROR: The setup on the server stopped with an error. Read the messages above.
    pause
    exit /b 1
)
echo.
echo All done. Open https://%SERVER% on the tablet.
pause
