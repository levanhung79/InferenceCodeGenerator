#!/bin/bash
# Setup script for ONNX Code Generator
# Handles PEP 668 (externally-managed-environment) on modern Linux systems

set -e

echo "ONNX Code Generator v4 - Setup Script"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    echo "Install with: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

python3 --version

# Check if venv module is available
if ! python3 -m venv --help &> /dev/null; then
    echo ""
    echo "Error: python3-venv not found"
    echo "Install with: sudo apt install python3-venv"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Verify activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

echo "Virtual environment activated: $VIRTUAL_ENV"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install package
echo ""
echo "Installing ONNX Code Generator..."
if [ "$1" == "--gui" ] || [ "$1" == "gui" ]; then
    echo "Installing with GUI support..."
    pip install -e ".[gui]"
else
    echo "Installing without GUI..."
    pip install -e .
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To activate the virtual environment in the future:"
echo "  cd $(pwd)"
echo "  source venv/bin/activate"
echo ""
echo "To use the tool:"
echo "  python -m onnx_codegen --check-env    # Check dependencies"
echo "  python -m onnx_codegen                # Launch GUI"
echo "  python -m onnx_codegen --cli          # Use CLI"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
