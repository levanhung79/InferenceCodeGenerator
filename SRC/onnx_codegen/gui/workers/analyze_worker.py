"""
Analysis Worker Thread.

Performs ONNX model analysis in background thread.
"""

try:
    from PySide6.QtCore import QThread, Signal
except ImportError:
    print("Error: PySide6 not installed")
    import sys
    sys.exit(1)

from ...core.analyzer import ONNXAnalyzer, ONNXModelInfo
from ...core.detector import ArchitectureDetector, DetectionResult
from ...core.errors import ONNXCodeGenError


class AnalyzeWorker(QThread):
    """Worker thread for analyzing ONNX models."""
    
    progress = Signal(int, str)  # percent, message
    finished = Signal(object, object)  # model_info, detection_result
    error = Signal(str)  # error message
    
    def __init__(self, model_path: str, parent=None):
        super().__init__(parent)
        self.model_path = model_path
    
    def run(self):
        """Run analysis in background thread."""
        try:
            # Analyze model
            self.progress.emit(10, "Loading ONNX model...")
            analyzer = ONNXAnalyzer(self.model_path)
            
            self.progress.emit(30, "Analyzing model structure...")
            model_info = analyzer.analyze(
                progress_callback=lambda p, m: self.progress.emit(30 + int(p * 0.4), m)
            )
            
            # Detect architecture
            self.progress.emit(70, "Detecting architecture...")
            detector = ArchitectureDetector(model_info)
            detection_result = detector.detect()
            
            self.progress.emit(100, "Analysis complete")
            
            # Emit results
            self.finished.emit(model_info, detection_result)
            
        except ONNXCodeGenError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Analysis failed: {str(e)}")

