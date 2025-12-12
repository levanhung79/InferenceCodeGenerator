# Linux Installation Guide

## Quick Setup (Recommended)

```bash
cd /mnt/d/DATA/PROJECTS/InferenceCodeGenerator/SRC

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install package
pip install --upgrade pip
pip install -e ".[gui]"
```

## Step-by-Step

### 1. Navigate to SRC directory

```bash
cd /mnt/d/DATA/PROJECTS/InferenceCodeGenerator/SRC
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

This creates an isolated Python environment in the `venv/` directory.

### 3. Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` in your prompt.

### 4. Upgrade pip

```bash
pip install --upgrade pip
```

### 5. Install Package

```bash
# Basic installation (CLI only)
pip install -e .

# With GUI support (recommended)
pip install -e ".[gui]"
```

### 6. Verify Installation

```bash
# Check environment
python -m onnx_codegen --check-env

# Test CLI
python -m onnx_codegen --cli --help
```

## Using the Tool

After installation, always activate the virtual environment first:

```bash
cd /mnt/d/DATA/PROJECTS/InferenceCodeGenerator/SRC
source venv/bin/activate

# Now you can use the tool
python -m onnx_codegen --check-env
python -m onnx_codegen              # GUI
python -m onnx_codegen --cli        # CLI
```

## Deactivate Virtual Environment

When done:

```bash
deactivate
```

## Alternative: Using pipx

If you prefer pipx (manages virtual environments automatically):

```bash
# Install pipx
sudo apt install pipx
pipx ensurepath

# Install package
cd /mnt/d/DATA/PROJECTS/InferenceCodeGenerator/SRC
pipx install -e ".[gui]"

# Use directly
onnx-codegen --check-env
```

## Troubleshooting

### "python3-venv not found"

```bash
sudo apt install python3-venv python3-pip
```

### "Permission denied" on setup.sh

```bash
chmod +x setup.sh
./setup.sh --gui
```

### Virtual environment activation doesn't work

Make sure you're using `source` (not `.`):

```bash
source venv/bin/activate  # Correct
. venv/bin/activate       # Also correct
venv/bin/activate         # Wrong - won't work
```

### GUI doesn't start (X11 forwarding in WSL)

If using WSL and GUI doesn't work:

```bash
# Install X11 dependencies
sudo apt install libxcb-xinerama0 libxcb-cursor0

# Or use X410/VcXsrv for Windows X server
```

## Next Steps

See `QUICKSTART.md` for usage examples.

