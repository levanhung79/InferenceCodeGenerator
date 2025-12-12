"""
ONNX Inference Code Generator v4

A tool to generate C++/Python inference code from ONNX models
for mobile platforms (Android/iOS).

Two operating modes:
- Mode A: ONNX + Python code (Recommended, 95%+ confidence)
- Mode B: ONNX only (70-85% confidence)

Two interfaces:
- CLI: Command-line interface for automation
- GUI: PySide6-based graphical interface
"""

__version__ = "4.0.0"
__author__ = "ONNX CodeGen Team"

from .core.analyzer import ONNXAnalyzer, ONNXModelInfo, TensorInfo
from .core.detector import ArchitectureDetector, Architecture, DetectionResult
from .core.parser import PythonCodeParser, ParseResult
from .core.config import ModelConfig, PreprocessConfig, PostprocessConfig
from .core.errors import ONNXCodeGenError, ErrorCode, ErrorHandler

__all__ = [
    "ONNXAnalyzer",
    "ONNXModelInfo",
    "TensorInfo",
    "ArchitectureDetector",
    "Architecture",
    "DetectionResult",
    "PythonCodeParser",
    "ParseResult",
    "ModelConfig",
    "PreprocessConfig",
    "PostprocessConfig",
    "ONNXCodeGenError",
    "ErrorCode",
    "ErrorHandler",
]

