# Quick Start Guide

## Installation

### Step 1: Create Virtual Environment

**Linux/macOS (Native filesystem):**
```bash
cd SRC
python3 -m venv venv
source venv/bin/activate
```

**WSL/Windows filesystem (`/mnt/`):**
```bash
cd SRC
# Use --copies to avoid symlink issues
python3 -m venv --copies venv
source venv/bin/activate
```

**Windows:**
```bash
cd SRC
python -m venv venv
venv\Scripts\activate
```

### Step 2: Install Package

```bash
# Basic installation
pip install -e .

# With GUI support (recommended)
pip install -e ".[gui]"
```

### Alternative: Using pipx (Linux/macOS)

```bash
# Install pipx
sudo apt install pipx  # Ubuntu/Debian
# or
brew install pipx      # macOS

# Install package
cd SRC
pipx install -e ".[gui]"
```

**Note:** Modern Linux systems (Ubuntu 23.04+, Debian 12+) use PEP 668 to protect system Python. Always use a virtual environment or pipx.

## CLI Usage

### Basic Usage (Mode B - ONNX only)

```bash
python -m onnx_codegen --cli --onnx model.onnx --output output/
```

### With Python Code (Mode A - Recommended)

```bash
python -m onnx_codegen --cli \
    --onnx model.onnx \
    --python-code inference.py \
    --output output/
```

### Check Environment

```bash
python -m onnx_codegen --check-env
```

## GUI Usage

```bash
python -m onnx_codegen
```

### GUI Workflow

1. **Step 1: Input** - Select ONNX file (required), Python code (optional), Labels file (optional)
2. **Step 2: Analysis** - View model information and architecture detection
3. **Step 3: Configure** - Adjust preprocessing and postprocessing settings
4. **Step 4: Verify** - (Optional) Test with a sample image
5. **Step 5: Generate** - Generate and preview C++ code

## Generated Code Structure

```
output/
├── detector.hpp          # Detector class header
├── detector.cpp          # Detector implementation
├── verify_single.cpp    # Main executable for testing
├── CMakeLists.txt       # Build configuration
└── README.md            # Build and usage instructions
```

## Building Generated Code

```bash
cd output/
mkdir build && cd build
cmake ..
make
./verify_single ../model.onnx ../test.jpg
```

## Output Files

- `<image>_result.jpg` - Image with bounding boxes drawn
- `<image>_result.txt` - YOLO format detection results

## Example Python Inference Code

For Mode A (ONNX + Python), provide a Python file like:

```python
import cv2
import onnxruntime as ort
import numpy as np

# Load model
session = ort.InferenceSession("model.onnx")

# Load and preprocess image
img = cv2.imread("test.jpg")
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img_resized = cv2.resize(img_rgb, (640, 640))
img_norm = img_resized.astype(np.float32) / 255.0
img_chw = np.transpose(img_norm, (2, 0, 1))
img_batch = np.expand_dims(img_chw, axis=0)

# Run inference
outputs = session.run(None, {"images": img_batch})

# Postprocess (NMS, threshold, etc.)
conf_threshold = 0.25
iou_threshold = 0.45
# ... NMS implementation ...
```

## Troubleshooting

### ONNX Runtime not found
```bash
pip install onnxruntime
```

### OpenCV not found (for building C++ code)
```bash
# Ubuntu/Debian
sudo apt install libopencv-dev

# macOS
brew install opencv
```

⚠️ **Note:** Python `opencv-python` package is **NOT sufficient** for building C++ code. You need system OpenCV C++ libraries (`libopencv-dev` on Linux).

### CMake not found (for building C++ code)
```bash
# Ubuntu/Debian
sudo apt install cmake

# macOS
brew install cmake
```

### Build Dependencies Summary
For detailed instructions on installing all build dependencies, see [INSTALL_BUILD_DEPS.md](INSTALL_BUILD_DEPS.md).

## Next Steps

1. Review generated code in `output/`
2. Build and test with your model
3. Customize postprocessing if needed
4. Extend for batch processing or video if required

