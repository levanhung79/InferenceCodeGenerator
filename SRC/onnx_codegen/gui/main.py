"""
GUI Application Entry Point.

Handles Qt platform initialization and launches main window.
"""

import sys
import os
from pathlib import Path

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
except ImportError:
    print("Error: PySide6 not installed. Please install: pip install PySide6")
    sys.exit(1)

from .main_window import MainWindow
from ..core.errors import ErrorHandler, create_error, ErrorCode


def setup_qt_platform():
    """Setup Qt platform plugins (handles Linux XCB issues)."""
    if sys.platform == "linux":
        # Check if running headless
        if not os.environ.get("DISPLAY"):
            # Try to use offscreen platform
            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        else:
            # Use xcb platform
            os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    
    # Set plugin path if needed
    if hasattr(QApplication, "setLibraryPaths"):
        plugin_path = Path(__file__).parent.parent.parent / "qt_plugins"
        if plugin_path.exists():
            QApplication.setLibraryPaths([str(plugin_path)])


def main():
    """Main GUI entry point."""
    setup_qt_platform()
    
    app = QApplication(sys.argv)
    app.setApplicationName("ONNX Code Generator")
    app.setApplicationVersion("4.0.0")
    app.setOrganizationName("ONNX CodeGen")
    
    # Enable high DPI scaling
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    try:
        window = MainWindow()
        window.show()
        return app.exec()
    except Exception as e:
        error = create_error(ErrorCode.UNKNOWN_ERROR, str(e))
        print(ErrorHandler.format_for_cli(error))
        return 1


if __name__ == "__main__":
    sys.exit(main())

