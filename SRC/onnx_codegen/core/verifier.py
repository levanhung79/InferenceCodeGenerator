"""
Verifier Module.

Verifies Python code (user-provided) and C++ code (tool-generated).
"""

import os
import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum
import re
import time

from .errors import create_error, ErrorCode


class VerificationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class Detection:
    """Detection result for comparison."""
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int
    class_name: str = ""


@dataclass
class VerificationResult:
    """Results from verification."""
    status: VerificationStatus
    detections: List[Detection] = field(default_factory=list)
    timing_ms: float = 0.0
    output_image_path: Optional[str] = None
    error_message: str = ""
    stdout: str = ""
    stderr: str = ""


@dataclass
class ComparisonResult:
    """Python vs C++ comparison results."""
    match: bool
    python_result: VerificationResult
    cpp_result: VerificationResult
    matched_pairs: int = 0
    summary: str = ""


class Verifier:
    """Verify Python and C++ code."""
    
    def verify_python(self, python_code_path: str, model_path: str, 
                     test_image_path: str, timeout: int = 60) -> VerificationResult:
        """Run Python code with test image."""
        result = VerificationResult(status=VerificationStatus.RUNNING)
        
        try:
            cmd = ["python", str(python_code_path), str(model_path), test_image_path]
            
            start = time.time()
            proc = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=timeout, cwd=str(Path(python_code_path).parent))
            result.timing_ms = (time.time() - start) * 1000
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            
            if proc.returncode != 0:
                result.status = VerificationStatus.FAILED
                result.error_message = f"Exit code {proc.returncode}"
                return result
            
            result.detections = self._parse_detections(proc.stdout)
            result.status = VerificationStatus.PASSED
            
        except subprocess.TimeoutExpired:
            result.status = VerificationStatus.ERROR
            result.error_message = f"Timeout after {timeout}s"
        except Exception as e:
            result.status = VerificationStatus.ERROR
            result.error_message = str(e)
        
        return result
    
    def verify_cpp(self, cpp_dir: str, model_path: str, test_image_path: str,
                   labels_path: Optional[str] = None, timeout: int = 120) -> VerificationResult:
        """Compile and run C++ code."""
        result = VerificationResult(status=VerificationStatus.RUNNING)
        
        try:
            # TODO: Implement C++ compilation and execution
            result.status = VerificationStatus.SKIPPED
            result.error_message = "C++ verification not yet implemented"
        except Exception as e:
            result.status = VerificationStatus.ERROR
            result.error_message = str(e)
        
        return result
    
    def compare(self, python_result: VerificationResult, 
                cpp_result: VerificationResult) -> ComparisonResult:
        """Compare Python and C++ results."""
        # TODO: Implement comparison logic
        return ComparisonResult(
            match=False,
            python_result=python_result,
            cpp_result=cpp_result,
            summary="Comparison not yet implemented"
        )
    
    def _parse_detections(self, stdout: str) -> List[Detection]:
        """Parse detections from stdout."""
        detections = []
        pattern = re.compile(r"(\w+)\s+([\d.]+)\s*\[([\d.,\s]+)\]")
        
        for line in stdout.split('\n'):
            match = pattern.search(line)
            if match:
                coords = [float(x.strip()) for x in match.group(3).split(',')]
                if len(coords) >= 4:
                    detections.append(Detection(
                        x1=coords[0], y1=coords[1], x2=coords[2], y2=coords[3],
                        confidence=float(match.group(2)), class_id=0, class_name=match.group(1)
                    ))
        return detections

