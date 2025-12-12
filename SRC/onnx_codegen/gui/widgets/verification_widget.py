"""
Verification Widget.

Allows user to verify generated code by running inference on test images.
"""

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
        QLabel, QFileDialog, QGroupBox, QTableWidget,
        QTableWidgetItem, QTextEdit, QMessageBox
    )
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QPixmap, QImage
except ImportError:
    print("Error: PySide6 not installed")
    import sys
    sys.exit(1)

from ...core.config import ModelConfig
from ...core.verifier import Verifier, VerificationResult, ComparisonResult


class VerificationWidget(QWidget):
    """Widget for verifying generated code."""
    
    verification_complete = Signal(object)  # ComparisonResult
    verification_failed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = None
        self._test_image_path = None
        self._verifier = Verifier()
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        # Instructions
        info_label = QLabel(
            "Step 3: Verify Generated Code\n\n"
            "Import a test image to verify that the generated C++ code produces "
            "the same results as Python inference (if available)."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(info_label)
        
        # Image selection
        image_group = QGroupBox("Test Image")
        image_layout = QHBoxLayout()
        
        self.image_path_label = QLabel("No image selected")
        self.image_path_label.setStyleSheet("padding: 5px;")
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_image)
        
        image_layout.addWidget(self.image_path_label)
        image_layout.addWidget(self.browse_btn)
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
        # Verification buttons
        verify_group = QGroupBox("Verification")
        verify_layout = QVBoxLayout()
        
        self.verify_python_btn = QPushButton("Verify Python Code")
        self.verify_python_btn.setEnabled(False)
        self.verify_python_btn.clicked.connect(self._verify_python)
        
        self.verify_cpp_btn = QPushButton("Verify C++ Code")
        self.verify_cpp_btn.setEnabled(False)
        self.verify_cpp_btn.clicked.connect(self._verify_cpp)
        
        verify_layout.addWidget(self.verify_python_btn)
        verify_layout.addWidget(self.verify_cpp_btn)
        verify_group.setLayout(verify_layout)
        layout.addWidget(verify_group)
        
        # Results display
        results_group = QGroupBox("Verification Results")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        results_layout.addWidget(self.results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.wrong_btn = QPushButton("✗ Results Wrong - Go Back")
        self.wrong_btn.setEnabled(False)
        self.wrong_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        self.wrong_btn.clicked.connect(self._on_wrong)
        
        self.correct_btn = QPushButton("✓ Results Correct - Continue")
        self.correct_btn.setEnabled(False)
        self.correct_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        self.correct_btn.clicked.connect(self._on_correct)
        
        action_layout.addWidget(self.wrong_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.correct_btn)
        layout.addLayout(action_layout)
        
        layout.addStretch()
    
    def set_config(self, config: ModelConfig):
        """Set configuration for verification."""
        self._config = config
        self._update_buttons()
    
    def _browse_image(self):
        """Browse for test image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Test Image",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp);;All Files (*)"
        )
        if file_path:
            self._test_image_path = file_path
            self.image_path_label.setText(file_path)
            self._update_buttons()
    
    def _update_buttons(self):
        """Update button states."""
        has_image = self._test_image_path is not None
        has_config = self._config is not None
        
        self.verify_python_btn.setEnabled(has_image and has_config)
        self.verify_cpp_btn.setEnabled(has_image and has_config)
    
    def _verify_python(self):
        """Verify Python code."""
        if not self._test_image_path or not self._config:
            return
        
        # TODO: Implement Python verification
        self.results_text.setText("Python verification not yet implemented.\n"
                                 "This will run the Python inference code and show results.")
    
    def _verify_cpp(self):
        """Verify C++ code."""
        if not self._test_image_path or not self._config:
            return
        
        # TODO: Implement C++ verification
        self.results_text.setText("C++ verification not yet implemented.\n"
                                 "This will compile and run the generated C++ code.")
    
    def _on_wrong(self):
        """Handle 'wrong' button click."""
        self.verification_failed.emit()
        QMessageBox.information(
            self,
            "Go Back",
            "Please review the configuration and try again."
        )
    
    def _on_correct(self):
        """Handle 'correct' button click."""
        # TODO: Compare results if both Python and C++ were run
        self.verification_complete.emit(None)

