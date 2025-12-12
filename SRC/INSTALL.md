# Installation Guide

## Quick Start

### Linux/macOS

```bash
cd SRC
chmod +x setup.sh
./setup.sh --gui
```

### Windows

```cmd
cd SRC
setup.bat --gui
```

## Manual Installation

### 1. Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install package
pip install -e .

# Or with GUI support
pip install -e ".[gui]"
```

## Why Virtual Environment?

Modern Linux distributions (Ubuntu 23.04+, Debian 12+) use **PEP 668** to protect system Python packages. This prevents installing packages directly to system Python, which could break system tools.

**Solutions:**
1. ✅ **Virtual Environment** (Recommended) - Isolated environment for the project
2. ✅ **pipx** - Manages virtual environments automatically
3. ❌ **--break-system-packages** - Not recommended, can break system

## Verification

After installation, verify everything works:

```bash
# Check environment
python -m onnx_codegen --check-env

# Test CLI
python -m onnx_codegen --cli --help

# Test GUI (if installed with [gui])
python -m onnx_codegen
```

## Troubleshooting

### "externally-managed-environment" Error

**Solution:** Use virtual environment (see above)

### "Python not found"

**Linux:**
```bash
sudo apt install python3 python3-venv python3-pip
```

**macOS:**
```bash
brew install python3
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/)

### "pip not found"

**Linux:**
```bash
sudo apt install python3-pip
```

**macOS:**
```bash
python3 -m ensurepip --upgrade
```

### GUI Dependencies Missing

If GUI doesn't work:

```bash
# Linux (Ubuntu/Debian)
sudo apt install python3-pyside6

# Or reinstall with GUI
pip install -e ".[gui]"
```

### ONNX Runtime Issues

```bash
# Install ONNX Runtime
pip install onnxruntime

# For GPU support (optional)
pip install onnxruntime-gpu
```

## Development Setup

For development with testing:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -e ".[gui,dev]"

# Run tests
pytest tests/
```

## Docker Installation (Alternative)

If you prefer Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY SRC/ /app/

RUN pip install --no-cache-dir -e ".[gui]"

CMD ["python", "-m", "onnx_codegen"]
```

Build and run:
```bash
docker build -t onnx-codegen .
docker run -it --rm -v $(pwd):/workspace onnx-codegen
```

