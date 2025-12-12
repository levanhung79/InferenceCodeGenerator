@echo off
REM Setup script for ONNX Code Generator (Windows)

echo ONNX Code Generator v4 - Setup Script
echo ======================================
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1 || (
    echo Error: Python not found
    exit /b 1
)

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install package
echo.
echo Installing ONNX Code Generator...
if "%1"=="--gui" (
    echo Installing with GUI support...
    pip install -e ".[gui]"
) else (
    echo Installing without GUI...
    pip install -e .
)

echo.
echo Installation complete!
echo.
echo To activate the virtual environment in the future:
echo   venv\Scripts\activate
echo.
echo To use the tool:
echo   python -m onnx_codegen --check-env
echo   python -m onnx_codegen              REM GUI
echo   python -m onnx_codegen --cli        REM CLI
echo.

