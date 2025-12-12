"""
Main Window for ONNX Code Generator GUI.

Implements the two-phase wizard workflow.
"""

try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QStackedWidget, QMessageBox,
        QStatusBar, QTabWidget, QFileDialog
    )
    from PySide6.QtCore import Qt, Slot
    from pathlib import Path
except ImportError:
    print("Error: PySide6 not installed")
    import sys
    sys.exit(1)

from ..core.errors import ErrorHandler, create_error, ErrorCode
from ..core.analyzer import ONNXAnalyzer
from ..core.config import ConfigBuilder, ModelConfig
from ..core.generator import CodeGenerator, TargetPlatform
from ..core.detector import ArchitectureDetector
from .widgets.file_picker import FilePickerWidget
from .widgets.analysis_view import AnalysisViewWidget
from .widgets.config_editor import ConfigEditorWidget
from .widgets.verification_widget import VerificationWidget
from .widgets.code_preview import CodePreviewWidget
from .widgets.progress_dialog import ProgressDialog
from .workers.analyze_worker import AnalyzeWorker
from .workers.generate_worker import GenerateWorker


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ONNX Inference Code Generator v4")
        self.setMinimumSize(1200, 800)
        
        # State
        self.current_model_path = None
        self.current_python_path = None
        self.current_labels_path = None
        self.current_config: ModelConfig = None
        self.current_model_info = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        # Central widget with tabs
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout(self.central_widget)
        
        # Title
        title = QLabel("ONNX Inference Code Generator v4")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Tabs for different steps
        self.tabs = QTabWidget()
        
        # Step 1: Input
        self.file_picker = FilePickerWidget()
        self.file_picker.onnx_file_changed.connect(self._on_onnx_file_changed)
        self.file_picker.python_file_changed.connect(self._on_python_file_changed)
        self.file_picker.labels_file_changed.connect(self._on_labels_file_changed)
        self.tabs.addTab(self.file_picker, "Step 1: Input")
        
        # Step 2: Analysis
        self.analysis_view = AnalysisViewWidget()
        self.tabs.addTab(self.analysis_view, "Step 2: Analysis")
        
        # Step 3: Configure
        self.config_editor = ConfigEditorWidget()
        self.config_editor.config_changed.connect(self._on_config_changed)
        self.tabs.addTab(self.config_editor, "Step 3: Configure")
        
        # Step 4: Verify (Optional)
        self.verification_widget = VerificationWidget()
        self.verification_widget.set_config(self.current_config)
        self.verification_widget.verification_complete.connect(self._on_verification_complete)
        self.verification_widget.verification_failed.connect(self._on_verification_failed)
        self.tabs.addTab(self.verification_widget, "Step 4: Verify (Optional)")
        
        # Step 5: Preview & Generate
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        self.code_preview = CodePreviewWidget()
        preview_layout.addWidget(self.code_preview)
        
        button_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Generate C++ Code")
        self.generate_btn.setEnabled(False)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.generate_btn.clicked.connect(self._on_generate_code)
        button_layout.addStretch()
        button_layout.addWidget(self.generate_btn)
        preview_layout.addLayout(button_layout)
        
        self.tabs.addTab(preview_widget, "Step 5: Generate")
        
        layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Select ONNX file to begin")
    
    @Slot(str)
    def _on_onnx_file_changed(self, file_path: str):
        """Handle ONNX file selection."""
        if not file_path:
            return
        
        self.current_model_path = file_path
        self.status_bar.showMessage(f"Analyzing: {Path(file_path).name}...")
        
        # Show progress and analyze
        progress = ProgressDialog("Analyzing Model", self)
        progress.show()
        
        self.analyze_worker = AnalyzeWorker(file_path)
        self.analyze_worker.progress.connect(progress.set_progress)
        self.analyze_worker.finished.connect(
            lambda info, detection: self._on_analysis_complete(info, detection, progress)
        )
        self.analyze_worker.error.connect(
            lambda msg: self._on_analysis_error(msg, progress)
        )
        self.analyze_worker.start()
    
    @Slot(str)
    def _on_python_file_changed(self, file_path: str):
        """Handle Python file selection."""
        self.current_python_path = file_path
        if file_path and self.current_config:
            # Rebuild config with Python code
            self._rebuild_config()
    
    @Slot(str)
    def _on_labels_file_changed(self, file_path: str):
        """Handle labels file selection."""
        self.current_labels_path = file_path
        if file_path and self.current_config:
            # Load labels
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    labels = [line.strip() for line in f if line.strip()]
                self.current_config.class_names = labels
            except Exception as e:
                QMessageBox.warning(self, "Load Labels Error", f"Failed to load labels: {e}")
    
    def _on_analysis_complete(self, model_info, detection, progress):
        """Handle analysis completion."""
        progress.close()
        
        self.current_model_info = model_info
        
        # Update analysis view
        self.analysis_view.set_model_info(model_info)
        self.analysis_view.set_detection_result(detection)
        
        # Build config
        from ..core.parser import PythonCodeParser
        parse_result = None
        if self.current_python_path:
            try:
                parser = PythonCodeParser(self.current_python_path)
                parse_result = parser.parse()
            except Exception as e:
                QMessageBox.warning(self, "Parse Warning", 
                                  f"Could not parse Python file:\n{e}")
        
        builder = ConfigBuilder(model_info, parse_result, detection)
        build_result = builder.build()
        self.current_config = build_result.config
        
        # Load labels if provided
        if self.current_labels_path:
            try:
                with open(self.current_labels_path, 'r', encoding='utf-8') as f:
                    labels = [line.strip() for line in f if line.strip()]
                self.current_config.class_names = labels
            except:
                pass
        
        # Update config editor
        self.config_editor.set_config(self.current_config)
        
        # Update verification widget
        self.verification_widget.set_config(self.current_config)
        
        # Enable generate button
        self.generate_btn.setEnabled(True)
        
        # Switch to analysis tab
        self.tabs.setCurrentIndex(1)
        
        self.status_bar.showMessage(
            f"Analyzed: {Path(self.current_model_path).name} - "
            f"{detection.architecture.name} ({detection.confidence:.0%})"
        )
    
    def _on_analysis_error(self, message, progress):
        """Handle analysis error."""
        progress.close()
        QMessageBox.critical(self, "Analysis Error", message)
        self.status_bar.showMessage("Analysis failed")
    
    def _rebuild_config(self):
        """Rebuild config with Python code."""
        if not self.current_model_info or not self.current_python_path:
            return
        
        from ..core.parser import PythonCodeParser
        from ..core.detector import ArchitectureDetector
        
        try:
            parser = PythonCodeParser(self.current_python_path)
            parse_result = parser.parse()
            
            detector = ArchitectureDetector(self.current_model_info)
            detection = detector.detect()
            
            builder = ConfigBuilder(self.current_model_info, parse_result, detection)
            build_result = builder.build()
            self.current_config = build_result.config
            
            self.config_editor.set_config(self.current_config)
        except Exception as e:
            QMessageBox.warning(self, "Config Update Error", f"Failed to update config: {e}")
    
    @Slot()
    def _on_config_changed(self):
        """Handle configuration change."""
        if self.current_config:
            self.current_config = self.config_editor.get_config()
            # Update verification widget with new config
            self.verification_widget.set_config(self.current_config)
    
    def _on_verification_complete(self, result):
        """Handle verification completion."""
        # Verification passed, can proceed to generation
        self.status_bar.showMessage("Verification passed - ready to generate")
    
    def _on_verification_failed(self):
        """Handle verification failure."""
        # Go back to configure step
        self.tabs.setCurrentIndex(2)  # Step 3: Configure
        self.status_bar.showMessage("Verification failed - please review configuration")
    
    @Slot()
    def _on_generate_code(self):
        """Generate C++ code."""
        if not self.current_config:
            QMessageBox.warning(self, "No Config", "Please analyze a model first")
            return
        
        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory"
        )
        
        if not output_dir:
            return
        
        # Show progress
        progress = ProgressDialog("Generating Code", self)
        progress.show()
        
        # Generate code
        generator = CodeGenerator(self.current_config)
        self.generate_worker = GenerateWorker(
            self.current_config,
            TargetPlatform.PC_OPENCV,
            output_dir
        )
        self.generate_worker.progress.connect(progress.set_progress)
        self.generate_worker.finished.connect(
            lambda result: self._on_generation_complete(result, progress)
        )
        self.generate_worker.error.connect(
            lambda msg: self._on_generation_error(msg, progress)
        )
        self.generate_worker.start()
    
    def _on_generation_complete(self, result, progress):
        """Handle generation completion."""
        progress.close()
        
        if result.success:
            self.code_preview.set_generated_files(result.files)
            self.tabs.setCurrentIndex(4)  # Switch to preview tab
            
            self.status_bar.showMessage(
                f"Generated {len(result.files)} files successfully"
            )
            
            QMessageBox.information(
                self,
                "Generation Complete",
                f"Successfully generated {len(result.files)} files!\n\n"
                f"Output directory: {result.output_dir}"
            )
        else:
            error_msg = "\n".join(result.errors)
            QMessageBox.critical(self, "Generation Failed", error_msg)
    
    def _on_generation_error(self, message, progress):
        """Handle generation error."""
        progress.close()
        QMessageBox.critical(self, "Generation Error", message)
        self.status_bar.showMessage("Generation failed")
    
    def show_error(self, error):
        """Show error message."""
        QMessageBox.critical(self, "Error", ErrorHandler.format_for_gui(error))

