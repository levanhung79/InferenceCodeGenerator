"""
Command-line interface for ONNX Code Generator.
"""

import argparse
import sys
from pathlib import Path

from ..core.analyzer import ONNXAnalyzer
from ..core.detector import ArchitectureDetector
from ..core.parser import PythonCodeParser
from ..core.config import ConfigBuilder
from ..core.generator import CodeGenerator, TargetPlatform
from ..core.errors import ErrorHandler, create_error, ErrorCode


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ONNX Inference Code Generator v4 - CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--onnx",
        required=True,
        help="Path to ONNX model file"
    )
    
    parser.add_argument(
        "--python-code",
        help="Path to Python inference code (optional, Mode A)"
    )
    
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory for generated code"
    )
    
    parser.add_argument(
        "--platform",
        choices=["pc_opencv", "pc_stb", "android", "ios"],
        default="pc_opencv",
        help="Target platform (default: pc_opencv)"
    )
    
    parser.add_argument(
        "--labels",
        help="Path to class labels file (one per line)"
    )
    
    args = parser.parse_args()
    
    try:
        # Analyze ONNX model
        print("Analyzing ONNX model...")
        analyzer = ONNXAnalyzer(args.onnx)
        model_info = analyzer.analyze()
        
        print(f"Model: {model_info.file_path}")
        print(f"Inputs: {len(model_info.inputs)}")
        print(f"Outputs: {len(model_info.outputs)}")
        
        # Parse Python code if provided
        parse_result = None
        if args.python_code:
            print("Parsing Python code...")
            parser = PythonCodeParser(args.python_code)
            parse_result = parser.parse()
            if not parse_result.success:
                print(f"Warning: Python parsing had errors: {parse_result.errors}")
        
        # Detect architecture
        print("Detecting architecture...")
        detector = ArchitectureDetector(model_info)
        detection_result = detector.detect()
        
        print(f"Architecture: {detection_result.architecture.name}")
        print(f"Confidence: {detection_result.confidence:.2%}")
        
        # Build config
        print("Building configuration...")
        builder = ConfigBuilder(model_info, parse_result, detection_result)
        build_result = builder.build()
        
        print(f"Config source: {build_result.source}")
        print(f"Config confidence: {build_result.confidence:.2%}")
        
        # Generate code
        print("Generating code...")
        generator = CodeGenerator(build_result.config)
        
        platform_map = {
            "pc_opencv": TargetPlatform.PC_OPENCV,
            "pc_stb": TargetPlatform.PC_STB,
            "android": TargetPlatform.ANDROID,
            "ios": TargetPlatform.IOS,
        }
        
        result = generator.generate(
            platform=platform_map[args.platform],
            output_dir=args.output
        )
        
        if result.success:
            print(f"\n✅ Code generation successful!")
            print(f"Generated {len(result.files)} files in {args.output}")
            for f in result.files:
                print(f"  - {f.path}: {f.description}")
        else:
            print(f"\n❌ Code generation failed:")
            for error in result.errors:
                print(f"  - {error}")
            return 1
        
        return 0
        
    except Exception as e:
        error = create_error(ErrorCode.UNKNOWN_ERROR, str(e))
        print(ErrorHandler.format_for_cli(error))
        return 1


if __name__ == "__main__":
    sys.exit(main())

