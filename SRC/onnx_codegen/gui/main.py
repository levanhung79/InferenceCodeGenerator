"""
GUI Application Entry Point.

Handles Qt platform initialization and launches main window.
"""

import sys
import os
import ctypes
from pathlib import Path

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
except ImportError:
    print("Error: PySide6 not installed. Please install: pip install PySide6")
    sys.exit(1)

from .main_window import MainWindow
from ..core.errors import ErrorHandler, create_error, ErrorCode


def check_xcb_dependencies():
    """
    Check if XCB dependencies are available.
    Returns list of missing libraries.
    """
    if sys.platform != "linux":
        return []
    
    required_libs = [
        "libxcb.so.1",
        "libxcb-xinerama.so.0",
        "libxcb-cursor.so.0",
        "libxkbcommon-x11.so.0",
    ]
    
    missing = []
    for lib in required_libs:
        try:
            ctypes.CDLL(lib)
        except OSError:
            missing.append(lib)
    
    return missing


def setup_qt_platform():
    """Setup Qt platform plugins (handles Linux XCB issues)."""
    if sys.platform == "linux":
        # Check if running headless
        if not os.environ.get("DISPLAY"):
            print("⚠️  No DISPLAY environment variable set.")
            print("   GUI requires X11 forwarding in WSL.")
            print("   See INSTALL_WSL.md for setup instructions.")
            print("   Falling back to offscreen mode (GUI will not be visible).")
            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        else:
            # Check XCB dependencies
            missing_libs = check_xcb_dependencies()
            if missing_libs:
                print("⚠️  Missing XCB libraries required for GUI:")
                for lib in missing_libs:
                    print(f"   - {lib}")
                print("\n   Install with:")
                print("   sudo apt install libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11")
                print("\n   Or use CLI mode: python -m onnx_codegen --cli")
                print("\n   Attempting to continue...\n")
            # Use xcb platform
            os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    
    # Set plugin path if needed
    if hasattr(QApplication, "setLibraryPaths"):
        plugin_path = Path(__file__).parent.parent.parent / "qt_plugins"
        if plugin_path.exists():
            QApplication.setLibraryPaths([str(plugin_path)])


def main():
    """Main GUI entry point."""
    # Setup platform before creating QApplication
    setup_qt_platform()
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("ONNX Code Generator")
        app.setApplicationVersion("4.0.0")
        app.setOrganizationName("ONNX CodeGen")
        
        # Enable high DPI scaling
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        window = MainWindow()
        window.show()
        return app.exec()
    except Exception as e:
        error_msg = str(e)
        
        # Check for common Qt/X11 errors
        if "xcb" in error_msg.lower() or "qt platform plugin" in error_msg.lower():
            print("\n" + "=" * 70)
            print("❌ Qt/X11 Platform Error")
            print("=" * 70)
            print("\nThe GUI requires X11 forwarding to work in WSL.")
            print("\nQuick Fix Options:")
            print("1. Install X11 dependencies:")
            print("   sudo apt install libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11")
            print("\n2. Set up X11 forwarding (see INSTALL_WSL.md)")
            print("\n3. Use CLI mode instead:")
            print("   python -m onnx_codegen --cli --onnx model.onnx --output output/")
            print("\n" + "=" * 70 + "\n")
        else:
            error = create_error(ErrorCode.UNKNOWN_ERROR, error_msg)
            print(ErrorHandler.format_for_cli(error))
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

