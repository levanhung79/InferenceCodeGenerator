# Building Generated C++ Code - Dependencies

The ONNX Code Generator creates C++ code that needs to be compiled. This requires additional system dependencies beyond the Python package.

## Required Dependencies

### 1. CMake (Build System)

CMake is required to build the generated C++ projects.

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install cmake
```

#### macOS
```bash
brew install cmake
```

#### Windows
1. Download from [cmake.org](https://cmake.org/download/)
2. Run the installer
3. Add CMake to PATH during installation

#### Verify Installation
```bash
cmake --version
# Should show: cmake version 3.x.x
```

### 2. C++ Compiler

A C++17 compatible compiler is required.

#### Ubuntu/Debian
```bash
sudo apt install build-essential
# This installs g++ (GNU C++ compiler)
```

#### macOS
```bash
# Xcode Command Line Tools (usually pre-installed)
xcode-select --install
```

#### Windows
- Install Visual Studio 2019 or later
- Or install MinGW-w64

#### Verify Installation
```bash
# Linux/macOS
g++ --version
# or
clang++ --version

# Windows (in Developer Command Prompt)
cl
```

### 3. OpenCV C++ Libraries

⚠️ **Important:** The Python `opencv-python` package is **NOT sufficient** for building C++ code. You need the actual OpenCV C++ libraries installed on your system.

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install libopencv-dev
```

This installs:
- OpenCV headers (`/usr/include/opencv4/`)
- OpenCV libraries (`/usr/lib/x86_64-linux-gnu/libopencv_*.so`)
- pkg-config support

#### macOS
```bash
brew install opencv
```

This installs OpenCV with pkg-config support.

#### Windows
1. Download OpenCV from [opencv.org/releases](https://opencv.org/releases/)
2. Extract to a location (e.g., `C:\opencv`)
3. Set environment variable:
   ```cmd
   set OpenCV_DIR=C:\opencv\build
   ```
4. Add to PATH:
   ```cmd
   set PATH=%PATH%;C:\opencv\build\x64\vc16\bin
   ```

#### Verify Installation

**Linux/macOS (with pkg-config):**
```bash
pkg-config --modversion opencv4
# Should show: 4.x.x
```

**Or check headers:**
```bash
# Linux
ls /usr/include/opencv4/

# macOS
ls /opt/homebrew/include/opencv4/  # Apple Silicon
# or
ls /usr/local/include/opencv4/     # Intel
```

### 4. ONNX Runtime C++ Libraries

The generated C++ code uses ONNX Runtime for inference.

#### Option 1: Download Pre-built (Recommended)

1. Download from [ONNX Runtime releases](https://github.com/microsoft/onnxruntime/releases)
2. Extract to a location (e.g., `~/onnxruntime`)
3. Set environment variable:
   ```bash
   export ONNXRUNTIME_ROOT=~/onnxruntime
   ```

#### Option 2: Build from Source

See [ONNX Runtime build instructions](https://onnxruntime.ai/docs/build/inferencing.html)

#### Verify Installation
```bash
# Check if ONNXRUNTIME_ROOT is set
echo $ONNXRUNTIME_ROOT

# Check if libraries exist
ls $ONNXRUNTIME_ROOT/lib/
```

## Quick Install Script (Ubuntu/Debian)

```bash
#!/bin/bash
# Install all build dependencies for Ubuntu/Debian

sudo apt update
sudo apt install -y \
    cmake \
    build-essential \
    libopencv-dev \
    pkg-config

echo "✅ Build dependencies installed!"
echo ""
echo "Next steps:"
echo "1. Download ONNX Runtime from: https://github.com/microsoft/onnxruntime/releases"
echo "2. Extract and set ONNXRUNTIME_ROOT environment variable"
echo "3. Generate C++ code with: python -m onnx_codegen --cli --onnx model.onnx --output output/"
echo "4. Build with: cd output && mkdir build && cd build && cmake .. && make"
```

## Building Generated Code

After installing dependencies:

```bash
# Generate code
python -m onnx_codegen --cli --onnx model.onnx --output output/

# Build
cd output/
mkdir build && cd build
cmake ..
make

# Run
./verify_single ../model.onnx ../test.jpg
```

## Troubleshooting

### CMake not found
```bash
# Ubuntu/Debian
sudo apt install cmake

# macOS
brew install cmake
```

### OpenCV not found by CMake

**Linux:**
```bash
# Install OpenCV
sudo apt install libopencv-dev

# Verify pkg-config
pkg-config --modversion opencv4
```

**macOS:**
```bash
brew install opencv
# CMake should find it automatically via pkg-config
```

**Windows:**
- Set `OpenCV_DIR` environment variable to OpenCV build directory
- Or specify in CMake:
  ```bash
  cmake -DOpenCV_DIR=C:/opencv/build ..
  ```

### ONNX Runtime not found

Set the `ONNXRUNTIME_ROOT` environment variable:

```bash
# Linux/macOS
export ONNXRUNTIME_ROOT=/path/to/onnxruntime

# Windows
set ONNXRUNTIME_ROOT=C:\path\to\onnxruntime
```

Or specify in CMake:
```bash
cmake -DONNXRUNTIME_ROOT=/path/to/onnxruntime ..
```

### "C++17 not supported"

Update your compiler:
- **g++**: Version 7+ required
- **clang++**: Version 5+ required
- **MSVC**: Visual Studio 2017+ required

```bash
# Ubuntu/Debian
sudo apt install g++-9  # or newer

# Use specific version
CXX=g++-9 cmake ..
```

## Summary

| Dependency | Purpose | Install Command |
|------------|---------|----------------|
| **CMake** | Build system | `sudo apt install cmake` (Linux)<br>`brew install cmake` (macOS) |
| **C++ Compiler** | Compile C++ code | `sudo apt install build-essential` (Linux)<br>`xcode-select --install` (macOS) |
| **OpenCV C++** | Image processing | `sudo apt install libopencv-dev` (Linux)<br>`brew install opencv` (macOS) |
| **ONNX Runtime C++** | Inference engine | Download from [releases](https://github.com/microsoft/onnxruntime/releases) |

**Note:** Python `opencv-python` is only for the Python tool itself, not for building C++ code.

