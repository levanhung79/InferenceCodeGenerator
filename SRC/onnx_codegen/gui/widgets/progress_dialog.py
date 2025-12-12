"""
Progress Dialog Widget.

Shows progress for long-running operations.
"""

try:
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
    from PySide6.QtCore import Qt
except ImportError:
    print("Error: PySide6 not installed")
    import sys
    sys.exit(1)


class ProgressDialog(QDialog):
    """Dialog for showing operation progress."""
    
    def __init__(self, title: str = "Processing...", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        self.message_label = QLabel("Initializing...")
        layout.addWidget(self.message_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
    
    def set_progress(self, percent: int, message: str = ""):
        """Update progress."""
        self.progress_bar.setValue(percent)
        if message:
            self.message_label.setText(message)
    
    def set_message(self, message: str):
        """Set progress message."""
        self.message_label.setText(message)

