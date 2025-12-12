"""
Core modules for ONNX Code Generator.

These modules have no GUI dependencies and can be used as a library.
"""

from .analyzer import ONNXAnalyzer, ONNXModelInfo, TensorInfo
from .detector import ArchitectureDetector, Architecture, DetectionResult
from .parser import PythonCodeParser, ParseResult
from .config import (
    ModelConfig, PreprocessConfig, PostprocessConfig,
    ConfigBuilder, BuildResult
)
from .errors import ONNXCodeGenError, ErrorCode, ErrorHandler, create_error
from .generator import CodeGenerator, GenerationResult
from .verifier import Verifier, VerificationResult, ComparisonResult

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
    "ConfigBuilder",
    "BuildResult",
    "ONNXCodeGenError",
    "ErrorCode",
    "ErrorHandler",
    "create_error",
    "CodeGenerator",
    "GenerationResult",
    "Verifier",
    "VerificationResult",
    "ComparisonResult",
]

