@echo off
REM ============================================================
REM  EQUITY DASHBOARD - one-click launcher (Windows)
REM  Just double-click this file. Leave the black window open.
REM ============================================================
title Equity Dashboard
cd /d "%~dp0"
setlocal
set "PYTHONIOENCODING=utf-8"

echo(
echo   ============================================
echo     EQUITY DASHBOARD - starting up...
echo   ============================================
echo(

REM -- 1. find Python (py launcher, then python on PATH, then known folder) --
set "PY="
where py >nul 2>&1 && set "PY=py"
if not defined PY ( where python >nul 2>&1 && set "PY=python" )
if not defined PY if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" set "PY=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"

if not defined PY (
  echo   [X] Python was not found on this computer.
  echo       Install Python 3.10 or newer from https://www.python.org/downloads/
  echo       During install, TICK "Add Python to PATH", then run this file again.
  echo(
  pause
  exit /b 1
)
echo   [1/3] Found Python: %PY%

REM -- 2. make sure the needed libraries are installed (only installs if missing) --
%PY% -c "import flask, flask_cors, yfinance, curl_cffi" >nul 2>&1
if errorlevel 1 (
  echo   [2/3] Installing required libraries ^(first run only, please wait^)...
  %PY% -m pip install --quiet -r requirements.txt
) else (
  echo   [2/3] Libraries already installed.
)

REM -- 3. open the browser, then start the server --
echo   [3/3] Opening your browser and starting the server...
echo(
echo   ------------------------------------------------------------
echo     Dashboard address:  http://127.0.0.1:5000
echo     KEEP THIS WINDOW OPEN while you use the dashboard.
echo     To STOP: close this window, or press Ctrl+C.
echo   ------------------------------------------------------------
echo(
start "" "http://127.0.0.1:5000"
%PY% server.py

echo(
echo   The server has stopped.
pause
endlocal
