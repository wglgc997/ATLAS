@echo off
setlocal
cd /d "%~dp0"

title Link Checker - Installation

echo ========================================
echo        LINK CHECKER INSTALLATION
echo ========================================
echo.

where py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found.
    echo Install Python and enable "Add Python to PATH".
    pause
    exit /b 1
)

echo Checking Python...
py --version
if errorlevel 1 (
    echo [ERROR] Python could not be executed.
    pause
    exit /b 1
)

if exist ".venv" (
    echo Removing previous virtual environment...
    rmdir /s /q ".venv"

    if exist ".venv" (
        echo [ERROR] Could not remove the previous .venv folder.
        echo Close Python processes and try again.
        pause
        exit /b 1
    )
)

echo Creating virtual environment...
py -m venv ".venv"
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

set "PYTHON=.venv\Scripts\python.exe"

echo Repairing pip...
"%PYTHON%" -m ensurepip --upgrade
if errorlevel 1 (
    echo [ERROR] Failed to install pip.
    pause
    exit /b 1
)

echo Updating pip...
"%PYTHON%" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [WARNING] Failed to update pip.
    echo Trying to continue with the bundled version...
)

echo Installing dependencies...
"%PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install project dependencies.
    echo This may be caused by:
    echo - Corporate proxy or certificate restrictions
    echo - Missing access to pypi.org
    echo - Antivirus blocking Python files
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully.
echo ========================================
pause