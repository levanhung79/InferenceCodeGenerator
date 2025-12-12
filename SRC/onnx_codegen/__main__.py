"""
Entry point for ONNX Code Generator.

Usage:
    python -m onnx_codegen          # Launch GUI
    python -m onnx_codegen --cli    # Launch CLI
    python -m onnx_codegen --check-env  # Check environment
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from onnx_codegen.cli.main import main as cli_main
from onnx_codegen.core.errors import ErrorCode, create_error, ErrorHandler
from onnx_codegen.core.environment import EnvironmentChecker


def check_environment():
    """Check if all required dependencies are available."""
    checker = EnvironmentChecker()
    result = checker.check_all()
    
    print("Environment Check Results:")
    print("=" * 60)
    
    for component, status in result.items():
        status_icon = "✅" if status.available else "❌"
        print(f"{status_icon} {component}: {status.message}")
        if not status.available and status.suggestions:
            for suggestion in status.suggestions:
                print(f"   💡 {suggestion}")
    
    print("=" * 60)
    
    all_ok = all(s.available for s in result.values() if s.required)
    return 0 if all_ok else 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ONNX Inference Code Generator v4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch GUI
  python -m onnx_codegen

  # Use CLI
  python -m onnx_codegen --cli --onnx model.onnx --output output/

  # Check environment
  python -m onnx_codegen --check-env
        """
    )
    
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Use command-line interface instead of GUI"
    )
    
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Check if all required dependencies are available"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 4.0.0"
    )
    
    args = parser.parse_args()
    
    if args.check_env:
        return check_environment()
    
    if args.cli:
        return cli_main()
    else:
        # Launch GUI
        try:
            from onnx_codegen.gui.main import main as gui_main
            return gui_main()
        except ImportError as e:
            print(f"Error: GUI dependencies not available: {e}")
            print("Please install PySide6: pip install PySide6")
            return 1
        except SystemExit as e:
            # Re-raise SystemExit from QApplication
            raise
        except Exception as e:
            error_msg = str(e)
            # Check for Qt/X11 platform errors
            if "xcb" in error_msg.lower() or "qt platform" in error_msg.lower():
                print("\n" + "=" * 70)
                print("❌ Qt/X11 Platform Error")
                print("=" * 70)
                print("\nThe GUI requires X11 dependencies and forwarding in WSL.")
                print("\nQuick Fix:")
                print("  sudo apt install libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11")
                print("\nOr use CLI mode:")
                print("  python -m onnx_codegen --cli --onnx model.onnx --output output/")
                print("\nSee INSTALL_WSL.md for detailed setup instructions.")
                print("=" * 70 + "\n")
            else:
                error = create_error(ErrorCode.UNKNOWN_ERROR, error_msg)
                print(ErrorHandler.format_for_cli(error))
            return 1


if __name__ == "__main__":
    sys.exit(main())

