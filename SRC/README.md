# ONNX Inference Code Generator v4

Generate C++/Python inference code from ONNX models for mobile platforms (Android/iOS).

## Features

- **Two Operating Modes**:
  - Mode A: ONNX + Python code (Recommended, 95%+ confidence)
  - Mode B: ONNX only (70-85% confidence)

- **Two Interfaces**:
  - CLI: Command-line interface for automation
  - GUI: PySide6-based graphical interface

- **Supported Platforms**:
  - PC/Desktop (OpenCV, stb_image, raw buffer)
  - Android (JNI + Kotlin)
  - iOS (ObjC++ bridge + Swift)

## Installation

```bash
# Install from source
cd SRC
pip install -e .

# With GUI support
pip install -e ".[gui]"
```

## Quick Start

### CLI Usage

```bash
# Basic usage (Mode B - ONNX only)
python -m onnx_codegen --cli --onnx model.onnx --output output/

# With Python code (Mode A - recommended)
python -m onnx_codegen --cli --onnx model.onnx --python-code inference.py --output output/

# Check environment
python -m onnx_codegen --check-env
```

### GUI Usage

```bash
# Launch GUI
python -m onnx_codegen
```

## Project Structure

```
onnx_codegen/
├── core/           # Core logic (no GUI dependencies)
│   ├── analyzer.py    # ONNX analysis
│   ├── detector.py    # Architecture detection
│   ├── parser.py      # Python code parsing
│   ├── config.py      # Config schema & builder
│   ├── generator.py   # Code generation
│   ├── verifier.py    # Verification logic
│   └── errors.py      # Error handling
├── cli/            # Command-line interface
├── gui/            # PySide6 GUI
└── templates/      # Code templates
```

## Requirements

- Python >= 3.9
- ONNX >= 1.14.0
- ONNX Runtime >= 1.16.0
- NumPy >= 1.24.0
- PySide6 >= 6.5.0 (for GUI)
- PyYAML >= 6.0
- Pillow >= 10.0.0

## License

MIT License

