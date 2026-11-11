@echo off
REM ============================================================
REM  Download every day's statistics from the AWS server, for the report.
REM  Saves them as stats-from-aws.json in the project folder.
REM  Run this on 11 Nov BEFORE deleting the stack.
REM ============================================================

REM The server's address. Change this if your DuckDNS name changes.
set SERVER=mysignlang.duckdns.org

title Download statistics
REM Work from the project folder (one level above this script).
cd /d "%~dp0.."

REM Ask for the login name. curl then asks for the password itself, without showing it.
set /p LOGIN=Login name:
curl -f -u "%LOGIN%" "https://%SERVER%/stats/all" -o stats-from-aws.json
if errorlevel 1 (
    echo ERROR: Could not download. Check the login and that the server is running.
    pause
    exit /b 1
)
echo.
echo Saved in stats-from-aws.json:
type stats-from-aws.json
echo.
pause
