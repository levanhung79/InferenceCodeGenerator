"""
File Picker Widget.

Allows user to select ONNX file and optional Python code file.
"""

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
        QLabel, QLineEdit, QFileDialog, QGroupBox
    )
    from PySide6.QtCore import Signal, Qt
except ImportError:
    print("Error: PySide6 not installed")
    import sys
    sys.exit(1)


class FilePickerWidget(QWidget):
    """Widget for selecting input files."""
    
    onnx_file_changed = Signal(str)
    python_file_changed = Signal(str)
    labels_file_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        # ONNX file selection
        onnx_group = QGroupBox("ONNX Model File (Required)")
        onnx_layout = QHBoxLayout()
        
        self.onnx_path_edit = QLineEdit()
        self.onnx_path_edit.setPlaceholderText("Select ONNX model file...")
        self.onnx_path_edit.setReadOnly(True)
        self.onnx_path_edit.textChanged.connect(
            lambda text: self.onnx_file_changed.emit(text)
        )
        
        self.onnx_browse_btn = QPushButton("Browse...")
        self.onnx_browse_btn.clicked.connect(self._browse_onnx)
        
        onnx_layout.addWidget(self.onnx_path_edit)
        onnx_layout.addWidget(self.onnx_browse_btn)
        onnx_group.setLayout(onnx_layout)
        layout.addWidget(onnx_group)
        
        # Python code file (optional)
        python_group = QGroupBox("Python Inference Code (Optional - Mode A)")
        python_layout = QHBoxLayout()
        
        self.python_path_edit = QLineEdit()
        self.python_path_edit.setPlaceholderText("Select Python inference code...")
        self.python_path_edit.setReadOnly(True)
        self.python_path_edit.textChanged.connect(
            lambda text: self.python_file_changed.emit(text)
        )
        
        self.python_browse_btn = QPushButton("Browse...")
        self.python_browse_btn.clicked.connect(self._browse_python)
        
        self.python_clear_btn = QPushButton("Clear")
        self.python_clear_btn.clicked.connect(self._clear_python)
        
        python_layout.addWidget(self.python_path_edit)
        python_layout.addWidget(self.python_browse_btn)
        python_layout.addWidget(self.python_clear_btn)
        python_group.setLayout(python_layout)
        layout.addWidget(python_group)
        
        # Labels file (optional)
        labels_group = QGroupBox("Class Labels File (Optional)")
        labels_layout = QHBoxLayout()
        
        self.labels_path_edit = QLineEdit()
        self.labels_path_edit.setPlaceholderText("Select labels file (one per line)...")
        self.labels_path_edit.setReadOnly(True)
        self.labels_path_edit.textChanged.connect(
            lambda text: self.labels_file_changed.emit(text)
        )
        
        self.labels_browse_btn = QPushButton("Browse...")
        self.labels_browse_btn.clicked.connect(self._browse_labels)
        
        self.labels_clear_btn = QPushButton("Clear")
        self.labels_clear_btn.clicked.connect(self._clear_labels)
        
        labels_layout.addWidget(self.labels_path_edit)
        labels_layout.addWidget(self.labels_browse_btn)
        labels_layout.addWidget(self.labels_clear_btn)
        labels_group.setLayout(labels_layout)
        layout.addWidget(labels_group)
        
        layout.addStretch()
    
    def _browse_onnx(self):
        """Browse for ONNX file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select ONNX Model File",
            "",
            "ONNX Files (*.onnx);;All Files (*)"
        )
        if file_path:
            self.set_onnx_file(file_path)
    
    def _browse_python(self):
        """Browse for Python file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Python Inference Code",
            "",
            "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.set_python_file(file_path)
    
    def _browse_labels(self):
        """Browse for labels file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Labels File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.set_labels_file(file_path)
    
    def _clear_python(self):
        """Clear Python file selection."""
        self.python_path_edit.clear()
    
    def _clear_labels(self):
        """Clear labels file selection."""
        self.labels_path_edit.clear()
    
    def set_onnx_file(self, file_path: str):
        """Set ONNX file path."""
        self.onnx_path_edit.setText(file_path)
    
    def set_python_file(self, file_path: str):
        """Set Python file path."""
        self.python_path_edit.setText(file_path)
    
    def set_labels_file(self, file_path: str):
        """Set labels file path."""
        self.labels_path_edit.setText(file_path)
    
    def get_onnx_file(self) -> str:
        """Get ONNX file path."""
        return self.onnx_path_edit.text()
    
    def get_python_file(self) -> str:
        """Get Python file path."""
        return self.python_path_edit.text()
    
    def get_labels_file(self) -> str:
        """Get labels file path."""
        return self.labels_path_edit.text()
    
    def has_onnx_file(self) -> bool:
        """Check if ONNX file is selected."""
        return bool(self.onnx_path_edit.text())

