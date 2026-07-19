@echo off
setlocal EnableExtensions

title Link Checker

REM Always run from the folder containing this BAT file.
cd /d "%~dp0"

echo ==================================================
echo Link Checker
echo ==================================================
echo.

REM ==================================================
REM 1. Find Python
REM ==================================================

set "PYTHON_CMD="

py -3.13 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.13"
    goto :python_found
)

python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :python_found
)

echo [ERROR] Python was not found.
echo.
echo Install Python 3.13 and run this file again.
echo Make sure Python is added to PATH.
echo.
pause
exit /b 1


:python_found

echo [OK] Python found:
%PYTHON_CMD% --version
echo.

REM ==================================================
REM 2. Create virtual environment
REM ==================================================

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creating virtual environment...

    %PYTHON_CMD% -m venv .venv

    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to create the virtual environment.
        echo Delete the .venv folder and try again.
        echo.
        pause
        exit /b 1
    )
) else (
    echo [OK] Virtual environment found.
)

set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"

echo.

REM ==================================================
REM 3. Install dependencies
REM ==================================================

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt was not found.
    echo.
    pause
    exit /b 1
)

echo [INFO] Updating pip...
"%VENV_PYTHON%" -m pip install --upgrade pip

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to update pip.
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] Installing project dependencies...
"%VENV_PYTHON%" -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install project dependencies.
    echo.
    pause
    exit /b 1
)

echo.

REM ==================================================
REM 4. Configure Playwright browser directory
REM ==================================================

set "PLAYWRIGHT_BROWSERS_PATH=%~dp0playwright-browsers"

echo [INFO] Playwright browser directory:
echo %PLAYWRIGHT_BROWSERS_PATH%
echo.

if not exist "%PLAYWRIGHT_BROWSERS_PATH%" (
    echo [INFO] Creating playwright-browsers directory...
    mkdir "%PLAYWRIGHT_BROWSERS_PATH%"

    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to create playwright-browsers.
        echo.
        pause
        exit /b 1
    )
)

echo [INFO] Installing or verifying Chromium...
"%VENV_PYTHON%" -m playwright install chromium

if errorlevel 1 (
    echo.
    echo [ERROR] Chromium installation failed.
    echo.
    echo Check:
    echo - Internet connection
    echo - Antivirus or firewall
    echo - Proxy or certificate restrictions
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Chromium is ready.
echo.

REM ==================================================
REM 5. Start application
REM ==================================================

if not exist "launcher.py" (
    echo [ERROR] launcher.py was not found.
    echo.
    pause
    exit /b 1
)

echo [INFO] Starting Link Checker...
echo.
echo Do not close this window while using the application.
echo ==================================================
echo.

"%VENV_PYTHON%" launcher.py

if errorlevel 1 (
    echo.
    echo ==================================================
    echo [ERROR] Link Checker stopped unexpectedly.
    echo ==================================================
    echo.
    pause
    exit /b 1
)

endlocal