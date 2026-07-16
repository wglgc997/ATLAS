@echo off
setlocal
cd /d "%~dp0"

title Link Checker

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Link Checker is not installed.
    echo Run install.bat first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" launcher.py

if errorlevel 1 (
    echo.
    echo [ERROR] Link Checker stopped with an error.
    pause
)