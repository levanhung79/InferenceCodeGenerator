"""
Setup script for ONNX Code Generator.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README if available
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="onnx-codegen",
    version="4.0.0",
    description="Generate C++/Python inference code from ONNX models for mobile platforms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ONNX CodeGen Team",
    author_email="",
    url="https://github.com/yourusername/onnx-codegen",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "onnx>=1.14.0",
        "onnxruntime>=1.16.0",
        "numpy>=1.24.0",
        "PyYAML>=6.0",
        "Pillow>=10.0.0",
    ],
    extras_require={
        "gui": ["PySide6>=6.5.0"],
        "dev": ["pytest>=7.0", "black", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "onnx-codegen=onnx_codegen.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)

