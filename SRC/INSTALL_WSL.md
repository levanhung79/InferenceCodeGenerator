# WSL Installation Guide

## Problem: Symlink Issues on Windows Filesystems

When using WSL with Windows filesystems mounted at `/mnt/`, Python's `venv` may fail with:
```
Error: [Errno 1] Operation not permitted: 'lib' -> 'venv/lib64'
```

This happens because Windows filesystems don't support Linux symlinks properly.

## Solutions

### Solution 1: Create Venv on Linux Filesystem (Recommended)

Even with `--copies`, Python's venv may still fail on Windows filesystems. Create the venv on the Linux filesystem instead:

```bash
cd /mnt/d/DATA/PROJECTS/InferenceCodeGenerator/SRC

# Create venv in Linux filesystem (home directory)
VENV_PATH="$HOME/.venvs/onnx-codegen"
mkdir -p "$HOME/.venvs"

# Remove old venv if exists
rm -rf "$VENV_PATH"

# Create venv on Linux filesystem
python3 -m venv "$VENV_PATH"

# Activate
source "$VENV_PATH/bin/activate"

# Install
pip install --upgrade pip
pip install -e ".[gui]"

# Create activation script in project directory for convenience
cat > venv_activate.sh << 'EOF'
#!/bin/bash
source "$HOME/.venvs/onnx-codegen/bin/activate"
EOF
chmod +x venv_activate.sh
```

Then in the future, just run:
```bash
source venv_activate.sh
```

### Solution 2: Use Updated Setup Script

The setup script now automatically detects Windows filesystems and creates the venv on Linux filesystem:

```bash
cd /mnt/d/DATA/PROJECTS/InferenceCodeGenerator/SRC
chmod +x setup.sh
./setup.sh --gui
```

The script will:
1. Detect that you're on a Windows filesystem (`/mnt/`)
2. Create venv at `~/.venvs/onnx-codegen-<project-name>`
3. Create a `venv_activate.sh` script in the project directory for easy activation

### Solution 3: Try --copies Flag (May Not Work)

Sometimes `--copies` works, but often it still fails:

```bash
cd /mnt/d/DATA/PROJECTS/InferenceCodeGenerator/SRC
rm -rf venv
python3 -m venv --copies venv
source venv/bin/activate
pip install -e ".[gui]"
```

If this fails with the same error, use Solution 1 instead.

## Manual Installation (Linux Filesystem)

If the setup script fails, create venv manually on Linux filesystem:

```bash
cd /mnt/d/DATA/PROJECTS/InferenceCodeGenerator/SRC

# Create venv in Linux filesystem
VENV_PATH="$HOME/.venvs/onnx-codegen"
mkdir -p "$HOME/.venvs"
rm -rf "$VENV_PATH"
python3 -m venv "$VENV_PATH"

# Activate
source "$VENV_PATH/bin/activate"

# Verify activation (should show venv path)
echo $VIRTUAL_ENV

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install package
pip install -e ".[gui]"

# Create activation script for convenience
cat > venv_activate.sh << 'EOF'
#!/bin/bash
source "$HOME/.venvs/onnx-codegen/bin/activate"
EOF
chmod +x venv_activate.sh
```

## Verify Installation

```bash
# Make sure venv is activated
source venv/bin/activate

# Check installation
python -m onnx_codegen --check-env

# Test CLI
python -m onnx_codegen --cli --help
```

## Using the Tool

Always activate the virtual environment first:

**If venv is in project directory:**
```bash
cd /mnt/d/DATA/PROJECTS/InferenceCodeGenerator/SRC
source venv/bin/activate
```

**If venv is on Linux filesystem (using activation script):**
```bash
cd /mnt/d/DATA/PROJECTS/InferenceCodeGenerator/SRC
source venv_activate.sh
```

**Or activate directly:**
```bash
source ~/.venvs/onnx-codegen/bin/activate
```

Then use the tool:
```bash
python -m onnx_codegen --check-env
python -m onnx_codegen              # GUI
python -m onnx_codegen --cli        # CLI
```

## Alternative: Use pipx

If venv continues to cause issues, use pipx:

```bash
# Install pipx
sudo apt install pipx
pipx ensurepath

# Install package (pipx manages its own venv)
cd /mnt/d/DATA/PROJECTS/InferenceCodeGenerator/SRC
pipx install -e ".[gui]"

# Use directly
onnx-codegen --check-env
```

## Troubleshooting

### Still getting permission errors

Try creating venv in your home directory:

```bash
# Create venv in home directory
python3 -m venv ~/venvs/onnx-codegen
source ~/venvs/onnx-codegen/bin/activate

# Install
cd /mnt/d/DATA/PROJECTS/InferenceCodeGenerator/SRC
pip install -e ".[gui]"
```

### "python3-venv not found"

```bash
sudo apt update
sudo apt install python3-venv python3-pip
```

### GUI doesn't work in WSL

The GUI requires X11 forwarding and XCB libraries. Here are your options:

#### Option 1: Install X11 Dependencies and Set Up X11 Forwarding (Recommended)

**Step 1: Install X11 dependencies**
```bash
sudo apt update
sudo apt install -y \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxkbcommon-x11 \
    libxcb1 \
    libx11-xcb1
```

**Step 2: Set up X11 forwarding**

Choose one of these methods:

**A. WSLg (Windows 11 only - Automatic)**
- WSLg is built into Windows 11
- Just install the dependencies above and run:
  ```bash
  python -m onnx_codegen
  ```

**B. VcXsrv (Windows 10/11 - Manual setup)**
1. Download and install [VcXsrv](https://sourceforge.net/projects/vcxsrv/)
2. Launch XLaunch with these settings:
   - Display number: 0
   - Start no client: ✓
   - Disable access control: ✓
   - Native opengl: ✓
3. In WSL, set DISPLAY:
   ```bash
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
   # Add to ~/.bashrc to make permanent:
   echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0' >> ~/.bashrc
   ```
4. Run GUI:
   ```bash
   python -m onnx_codegen
   ```

**C. X410 (Paid, but works well)**
1. Install X410 from Microsoft Store
2. Launch X410
3. In WSL:
   ```bash
   export DISPLAY=:0.0
   echo 'export DISPLAY=:0.0' >> ~/.bashrc
   ```
4. Run GUI:
   ```bash
   python -m onnx_codegen
   ```

#### Option 2: Use CLI Mode (No GUI needed)

If you don't need the GUI, use CLI mode instead:

```bash
# Basic usage
python -m onnx_codegen --cli --onnx model.onnx --output output/

# With Python code (recommended)
python -m onnx_codegen --cli --onnx model.onnx --python-code inference.py --output output/

# See help
python -m onnx_codegen --cli --help
```

#### Option 3: Use Virtual Framebuffer (Headless)

If you want to run GUI in headless mode (for testing):

```bash
# Install xvfb
sudo apt install xvfb

# Run with virtual framebuffer
xvfb-run python -m onnx_codegen
```

#### Troubleshooting GUI Issues

**Error: "Could not load the Qt platform plugin 'xcb'"**
```bash
# Install missing dependencies
sudo apt install libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11
```

**Error: "No DISPLAY environment variable"**
```bash
# Set DISPLAY (see Option 1 above for your X server)
export DISPLAY=:0.0  # For X410
# or
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0  # For VcXsrv
```

**Error: "Aborted (core dumped)"**
- Usually means missing XCB libraries
- Install: `sudo apt install libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11`

## Building Generated C++ Code

After generating C++ code, you'll need additional dependencies to build it:

### Required Build Dependencies

```bash
# Install CMake, compiler, and OpenCV C++ libraries
sudo apt update
sudo apt install cmake build-essential libopencv-dev

# Download ONNX Runtime C++ libraries
# See: https://github.com/microsoft/onnxruntime/releases
```

⚠️ **Important:** The Python `opencv-python` package is **NOT sufficient** for building C++ code. You need `libopencv-dev` (system OpenCV C++ libraries).

See [INSTALL_BUILD_DEPS.md](INSTALL_BUILD_DEPS.md) for detailed instructions.

