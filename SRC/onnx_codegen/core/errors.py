"""
Error handling for ONNX Code Generator.

Provides structured error codes, exceptions, and error formatting.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List


class ErrorCode(Enum):
    """Error codes for tool."""
    # Input errors (1xx)
    ONNX_NOT_FOUND = 101
    ONNX_INVALID = 102
    PYTHON_CODE_NOT_FOUND = 103
    PYTHON_CODE_INVALID = 104
    IMAGE_NOT_FOUND = 105
    IMAGE_INVALID = 106
    
    # Environment errors (2xx)
    OPENCV_NOT_FOUND = 201
    ONNXRUNTIME_NOT_FOUND = 202
    CMAKE_NOT_FOUND = 203
    COMPILER_NOT_FOUND = 204
    NDK_NOT_FOUND = 205
    XCODE_NOT_FOUND = 206
    
    # Parse errors (3xx)
    PYTHON_PARSE_FAILED = 301
    CONFIG_INVALID = 302
    
    # Generation errors (4xx)
    GENERATION_FAILED = 401
    OUTPUT_DIR_NOT_WRITABLE = 402
    
    # Verification errors (5xx)
    COMPILE_FAILED = 501
    RUN_FAILED = 502
    VERIFICATION_MISMATCH = 503
    VERIFICATION_TIMEOUT = 504
    
    # Architecture detection errors (6xx)
    ARCHITECTURE_LOW_CONFIDENCE = 601
    ARCHITECTURE_UNKNOWN = 602
    ARCHITECTURE_VALIDATION_FAILED = 603
    
    # Dynamic shape errors (7xx)
    DYNAMIC_SHAPE_UNSUPPORTED = 701
    DYNAMIC_SHAPE_MISSING_DEFAULT = 702
    
    # Template errors (8xx)
    TEMPLATE_MISSING_VARIABLE = 801
    TEMPLATE_RENDER_FAILED = 802
    
    # Unknown error
    UNKNOWN_ERROR = 999


@dataclass
class ONNXCodeGenError(Exception):
    """Base exception for ONNX CodeGen."""
    code: ErrorCode
    message: str
    details: Optional[str] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
    
    def __str__(self):
        return f"[{self.code.name}] {self.message}"
    
    def to_dict(self):
        return {
            "code": self.code.value,
            "name": self.code.name,
            "message": self.message,
            "details": self.details,
            "suggestions": self.suggestions
        }


# Predefined errors with suggestions
ERROR_TEMPLATES = {
    ErrorCode.ONNX_NOT_FOUND: {
        "message": "ONNX file not found",
        "suggestions": ["Check file path", "Ensure file has .onnx extension"]
    },
    ErrorCode.OPENCV_NOT_FOUND: {
        "message": "OpenCV not found",
        "suggestions": [
            "Install OpenCV: sudo apt install libopencv-dev",
            "Or use stb_image mode (no dependencies)"
        ]
    },
    ErrorCode.CMAKE_NOT_FOUND: {
        "message": "CMake not found",
        "suggestions": ["Install CMake: sudo apt install cmake"]
    },
    ErrorCode.COMPILE_FAILED: {
        "message": "C++ compilation failed",
        "suggestions": [
            "Check compiler is installed: g++ --version",
            "Check CMakeLists.txt syntax",
            "Check include paths for ONNX Runtime and OpenCV"
        ]
    },
    ErrorCode.VERIFICATION_MISMATCH: {
        "message": "Python and C++ results do not match",
        "suggestions": [
            "Check preprocessing config (resize, normalize, color format)",
            "Check postprocessing config (NMS threshold, confidence)",
            "Try with different test image"
        ]
    },
    ErrorCode.ARCHITECTURE_LOW_CONFIDENCE: {
        "message": "Architecture detection has low confidence",
        "suggestions": [
            "Review detected architecture and evidence",
            "Manually select architecture if incorrect",
            "Provide Python inference code for better accuracy"
        ]
    },
    ErrorCode.ARCHITECTURE_UNKNOWN: {
        "message": "Could not detect model architecture",
        "suggestions": [
            "Provide Python inference code (Mode A) for better results",
            "Manually configure preprocessing/postprocessing",
            "Use generic template and customize manually"
        ]
    },
    ErrorCode.DYNAMIC_SHAPE_UNSUPPORTED: {
        "message": "Model has dynamic shapes that may not be fully supported",
        "suggestions": [
            "Set default values for dynamic dimensions in config",
            "Review generated code for runtime shape handling",
            "Consider exporting model with fixed input shapes"
        ]
    },
    ErrorCode.TEMPLATE_MISSING_VARIABLE: {
        "message": "Template variable missing during code generation",
        "suggestions": [
            "Check config has all required fields",
            "Report this as a bug with model info"
        ]
    },
    ErrorCode.UNKNOWN_ERROR: {
        "message": "Unknown error occurred",
        "suggestions": ["Check logs for details", "Report this as a bug"]
    }
}


def create_error(code: ErrorCode, details: str = None) -> ONNXCodeGenError:
    """Create error from template."""
    template = ERROR_TEMPLATES.get(code, {"message": "Unknown error", "suggestions": []})
    return ONNXCodeGenError(
        code=code,
        message=template["message"],
        details=details,
        suggestions=template["suggestions"]
    )


class ErrorHandler:
    """Handler to display errors in GUI."""
    
    @staticmethod
    def format_for_gui(error: ONNXCodeGenError) -> str:
        """Format error for GUI display."""
        lines = [f"❌ {error.message}"]
        if error.details:
            lines.append(f"\nDetails: {error.details}")
        if error.suggestions:
            lines.append("\n💡 Suggestions:")
            for s in error.suggestions:
                lines.append(f"  • {s}")
        return "\n".join(lines)
    
    @staticmethod
    def format_for_cli(error: ONNXCodeGenError) -> str:
        """Format error for CLI output."""
        lines = [f"Error [{error.code.name}]: {error.message}"]
        if error.details:
            lines.append(f"  {error.details}")
        if error.suggestions:
            lines.append("Suggestions:")
            for s in error.suggestions:
                lines.append(f"  - {s}")
        return "\n".join(lines)

