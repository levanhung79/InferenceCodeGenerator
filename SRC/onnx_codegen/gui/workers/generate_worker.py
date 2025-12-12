"""
Code Generation Worker Thread.

Generates code in background thread.
"""

try:
    from PySide6.QtCore import QThread, Signal
except ImportError:
    print("Error: PySide6 not installed")
    import sys
    sys.exit(1)

from ...core.generator import CodeGenerator, GenerationResult, TargetPlatform
from ...core.config import ModelConfig
from ...core.errors import ONNXCodeGenError


class GenerateWorker(QThread):
    """Worker thread for generating code."""
    
    progress = Signal(int, str)  # percent, message
    finished = Signal(object)  # GenerationResult
    error = Signal(str)  # error message
    
    def __init__(self, config: ModelConfig, platform: TargetPlatform,
                 output_dir: str, parent=None):
        super().__init__(parent)
        self.config = config
        self.platform = platform
        self.output_dir = output_dir
    
    def run(self):
        """Run code generation in background thread."""
        try:
            generator = CodeGenerator(self.config)
            
            result = generator.generate(
                platform=self.platform,
                output_dir=self.output_dir,
                progress_callback=lambda p, m: self.progress.emit(p, m)
            )
            
            self.finished.emit(result)
            
        except ONNXCodeGenError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Generation failed: {str(e)}")

