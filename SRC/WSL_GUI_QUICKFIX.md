# WSL GUI Quick Fix

If you see this error:
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
This application failed to start because no Qt platform plugin could be initialized.
```

## Quick Fix (Choose One)

### Option 1: Install X11 Dependencies (Required)

```bash
sudo apt update
sudo apt install -y \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxkbcommon-x11 \
    libxcb1 \
    libx11-xcb1
```

### Option 2: Set Up X11 Forwarding

**For Windows 11 (WSLg - Automatic):**
- Just install dependencies above, no additional setup needed

**For Windows 10 (VcXsrv):**
1. Download [VcXsrv](https://sourceforge.net/projects/vcxsrv/)
2. Launch XLaunch with "Disable access control" enabled
3. In WSL:
   ```bash
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
   echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0' >> ~/.bashrc
   ```

**For X410 (Paid):**
1. Install from Microsoft Store
2. Launch X410
3. In WSL:
   ```bash
   export DISPLAY=:0.0
   echo 'export DISPLAY=:0.0' >> ~/.bashrc
   ```

### Option 3: Use CLI Mode (No GUI)

If you don't need the GUI:

```bash
python -m onnx_codegen --cli --onnx model.onnx --output output/
```

## Verify Setup

After installing dependencies and setting up X11:

```bash
# Check if DISPLAY is set
echo $DISPLAY

# Try running GUI
python -m onnx_codegen
```

## Still Having Issues?

See [INSTALL_WSL.md](INSTALL_WSL.md) for detailed troubleshooting.

