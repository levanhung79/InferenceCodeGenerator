"""
Environment Checker.

Checks if all required dependencies are available.
"""

import os
import shutil
import subprocess
import sys
import platform
from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class ComponentStatus:
    """Status of a component."""
    available: bool
    message: str
    required: bool = True
    suggestions: List[str] = field(default_factory=list)


class EnvironmentChecker:
    """Check environment for required dependencies."""
    
    def check_all(self) -> Dict[str, ComponentStatus]:
        """Check all components."""
        results = {}
        
        results["Python"] = self._check_python()
        results["ONNX"] = self._check_onnx()
        results["ONNX Runtime"] = self._check_onnxruntime()
        results["PySide6"] = self._check_pyside6()
        results["CMake"] = self._check_cmake()
        results["C++ Compiler"] = self._check_compiler()
        results["OpenCV"] = self._check_opencv()
        results["Android NDK"] = self._check_android_ndk()
        results["Xcode"] = self._check_xcode()
        
        return results
    
    def _check_python(self) -> ComponentStatus:
        """Check Python version."""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 9:
            return ComponentStatus(
                available=True,
                message=f"Python {version.major}.{version.minor}.{version.micro}"
            )
        return ComponentStatus(
            available=False,
            message=f"Python {version.major}.{version.minor} (requires 3.9+)",
            suggestions=["Upgrade Python to 3.9 or later"]
        )
    
    def _check_onnx(self) -> ComponentStatus:
        """Check ONNX package."""
        try:
            import onnx
            return ComponentStatus(
                available=True,
                message=f"ONNX {onnx.__version__}"
            )
        except ImportError:
            return ComponentStatus(
                available=False,
                message="ONNX not found",
                suggestions=["Install: pip install onnx"]
            )
    
    def _check_onnxruntime(self) -> ComponentStatus:
        """Check ONNX Runtime."""
        try:
            import onnxruntime as ort
            return ComponentStatus(
                available=True,
                message=f"ONNX Runtime {ort.__version__}"
            )
        except ImportError:
            return ComponentStatus(
                available=False,
                message="ONNX Runtime not found",
                suggestions=["Install: pip install onnxruntime"]
            )
    
    def _check_pyside6(self) -> ComponentStatus:
        """Check PySide6."""
        try:
            import PySide6
            return ComponentStatus(
                available=True,
                message=f"PySide6 {PySide6.__version__}",
                required=False  # Optional for CLI mode
            )
        except ImportError:
            return ComponentStatus(
                available=False,
                message="PySide6 not found (GUI will be unavailable)",
                required=False,
                suggestions=["Install: pip install PySide6"]
            )
    
    def _check_cmake(self) -> ComponentStatus:
        """Check CMake."""
        cmake_path = shutil.which("cmake")
        if cmake_path:
            try:
                result = subprocess.run(["cmake", "--version"], 
                                      capture_output=True, text=True, timeout=5)
                version = result.stdout.split('\n')[0] if result.returncode == 0 else "unknown"
                return ComponentStatus(
                    available=True,
                    message=version,
                    required=False  # Only needed for verification
                )
            except:
                pass
        
        return ComponentStatus(
            available=False,
            message="CMake not found",
            required=False,
            suggestions=["Install CMake for C++ code verification"]
        )
    
    def _check_compiler(self) -> ComponentStatus:
        """Check C++ compiler."""
        compilers = ["g++", "clang++", "cl"]
        for compiler in compilers:
            if shutil.which(compiler):
                return ComponentStatus(
                    available=True,
                    message=f"{compiler} found",
                    required=False
                )
        
        return ComponentStatus(
            available=False,
            message="C++ compiler not found",
            required=False,
            suggestions=["Install g++ or clang++ for C++ code verification"]
        )
    
    def _check_opencv(self) -> ComponentStatus:
        """Check OpenCV."""
        # Check Python OpenCV
        try:
            import cv2
            return ComponentStatus(
                available=True,
                message=f"OpenCV Python {cv2.__version__}",
                required=False
            )
        except ImportError:
            pass
        
        # Check system OpenCV (would need pkg-config or manual check)
        return ComponentStatus(
            available=False,
            message="OpenCV not found",
            required=False,
            suggestions=["Install: pip install opencv-python or system package"]
        )
    
    def _check_android_ndk(self) -> ComponentStatus:
        """Check Android NDK."""
        ndk_path = os.environ.get("ANDROID_NDK_HOME") or os.environ.get("ANDROID_NDK_ROOT")
        if ndk_path and os.path.exists(ndk_path):
            return ComponentStatus(
                available=True,
                message=f"Android NDK found at {ndk_path}",
                required=False
            )
        
        return ComponentStatus(
            available=False,
            message="Android NDK not found",
            required=False,
            suggestions=["Set ANDROID_NDK_HOME environment variable"]
        )
    
    def _check_xcode(self) -> ComponentStatus:
        """Check Xcode (macOS only)."""
        if platform.system() != "Darwin":
            return ComponentStatus(
                available=False,
                message="Xcode only available on macOS",
                required=False
            )
        
        xcode_path = shutil.which("xcodebuild")
        if xcode_path:
            return ComponentStatus(
                available=True,
                message="Xcode found",
                required=False
            )
        
        return ComponentStatus(
            available=False,
            message="Xcode not found",
            required=False,
            suggestions=["Install Xcode from App Store"]
        )

