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

# Check if we're on WSL/Windows filesystem (common issue with symlinks)
# Detect if we're on a Windows mount point
IS_WINDOWS_FS=false
if [[ "$(pwd)" == /mnt/* ]] || [[ "$(stat -f -c %T . 2>/dev/null)" == *"msdos"* ]] || [[ "$(df -T . | tail -1 | awk '{print $2}')" == *"fuseblk"* ]]; then
    IS_WINDOWS_FS=true
    echo "⚠️  Detected Windows filesystem (/mnt/). Symlinks may not work."
    echo "   Creating venv on Linux filesystem instead..."
fi

if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

if [ "$IS_WINDOWS_FS" = true ]; then
    # Create venv in Linux filesystem (home directory)
    VENV_PATH="$HOME/.venvs/onnx-codegen-$(basename $(pwd))"
    echo "Creating venv at: $VENV_PATH"
    
    # Create parent directory if needed
    mkdir -p "$HOME/.venvs"
    
    # Remove old venv if exists
    if [ -d "$VENV_PATH" ]; then
        rm -rf "$VENV_PATH"
    fi
    
    # Create venv on Linux filesystem
    python3 -m venv "$VENV_PATH"
    
    # Create a symlink or activation script in project directory
    echo "Creating activation script..."
    cat > venv_activate.sh << EOF
#!/bin/bash
# Auto-generated activation script for venv on Linux filesystem
source "$VENV_PATH/bin/activate"
EOF
    chmod +x venv_activate.sh
    
    # Activate the venv
    source "$VENV_PATH/bin/activate"
    
    # Store venv path for later use
    echo "$VENV_PATH" > .venv_path
    
    echo "✅ Virtual environment created on Linux filesystem"
    echo "   To activate in the future, run: source venv_activate.sh"
else
    # Use --copies flag to avoid symlink issues (for other edge cases)
    echo "Creating venv with --copies flag..."
    python3 -m venv --copies venv
    source venv/bin/activate
fi

# Verify activation (if not already activated above)
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    if [ -f "venv_activate.sh" ]; then
        source venv_activate.sh
    elif [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "Error: Virtual environment not found"
        exit 1
    fi
fi

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
if [ -f "venv_activate.sh" ]; then
    echo "  source venv_activate.sh          # (venv on Linux filesystem)"
else
    echo "  source venv/bin/activate         # (venv in project directory)"
fi
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
