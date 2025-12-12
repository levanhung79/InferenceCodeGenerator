"""
Code Preview Widget.

Shows preview of generated code.
"""

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
        QPushButton, QLabel, QFileDialog, QGroupBox
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont
except ImportError:
    print("Error: PySide6 not installed")
    import sys
    sys.exit(1)

from ...core.generator import GeneratedFile


class CodePreviewWidget(QWidget):
    """Widget for previewing generated code."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._generated_files = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        header_label = QLabel("Generated Code Preview")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header.addWidget(header_label)
        header.addStretch()
        
        self.save_btn = QPushButton("Save All Files...")
        self.save_btn.clicked.connect(self._save_all)
        header.addWidget(self.save_btn)
        
        layout.addLayout(header)
        
        # File selector
        file_group = QGroupBox("Select File to Preview")
        file_layout = QVBoxLayout()
        
        self.file_list = QTextEdit()
        self.file_list.setReadOnly(True)
        self.file_list.setMaximumHeight(100)
        self.file_list.setPlaceholderText("No files generated yet")
        file_layout.addWidget(self.file_list)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Code preview
        code_group = QGroupBox("Code Preview")
        code_layout = QVBoxLayout()
        
        self.code_text = QTextEdit()
        self.code_text.setReadOnly(True)
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier", 10)
        self.code_text.setFont(font)
        code_layout.addWidget(self.code_text)
        
        code_group.setLayout(code_layout)
        layout.addWidget(code_group)
    
    def set_generated_files(self, files: list[GeneratedFile]):
        """Set generated files to preview."""
        self._generated_files = files
        
        if not files:
            self.file_list.clear()
            self.code_text.clear()
            return
        
        # List files
        file_list_text = "\n".join([f"{i+1}. {f.path} - {f.description}" 
                                    for i, f in enumerate(files)])
        self.file_list.setText(file_list_text)
        
        # Show first file
        if files:
            self._show_file(0)
    
    def _show_file(self, index: int):
        """Show file at index."""
        if 0 <= index < len(self._generated_files):
            file = self._generated_files[index]
            self.code_text.setText(file.content)
    
    def _save_all(self):
        """Save all generated files."""
        if not self._generated_files:
            return
        
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory"
        )
        
        if not output_dir:
            return
        
        import os
        saved_count = 0
        for file in self._generated_files:
            file_path = os.path.join(output_dir, os.path.basename(file.path))
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file.content)
                saved_count += 1
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Save Error", 
                                  f"Failed to save {file_path}:\n{e}")
        
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Save Complete", 
                              f"Saved {saved_count} file(s) to {output_dir}")

