# ONNX Inference Code Generator v4

> **Goal**: Generate C++/Python inference code from ONNX model for mobile platforms (Android/iOS)  
> **Two operating modes**: ONNX-only mode and ONNX+Python mode  
> **Two interfaces**: CLI and GUI (PySide6)

---

## 1. Architecture Overview

### 1.1. Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ONNX INFERENCE CODE GENERATOR               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                   PRESENTATION LAYER                     │  │
│   │  ┌─────────────────┐       ┌─────────────────────────┐  │  │
│   │  │   CLI Interface │       │   GUI (PySide6)         │  │  │
│   │  │   (argparse)    │       │   - Main Window         │  │  │
│   │  │                 │       │   - Config Editor       │  │  │
│   │  │                 │       │   - Code Preview        │  │  │
│   │  └────────┬────────┘       └────────────┬────────────┘  │  │
│   └───────────┼─────────────────────────────┼───────────────┘  │
│               │                             │                   │
│               └──────────────┬──────────────┘                   │
│                              ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                      CORE LAYER                          │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │  │
│   │  │    ONNX     │  │   Python    │  │     Config      │  │  │
│   │  │  Analyzer   │  │   Parser    │  │     Builder     │  │  │
│   │  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘  │  │
│   │         │                │                   │           │  │
│   │         └────────────────┼───────────────────┘           │  │
│   │                          ▼                               │  │
│   │                 ┌─────────────────┐                      │  │
│   │                 │  Code Generator │                      │  │
│   │                 └────────┬────────┘                      │  │
│   └──────────────────────────┼──────────────────────────────┘  │
│                              ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                     OUTPUT LAYER                         │  │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │  │
│   │  │   C++    │  │  Python  │  │  Config  │  │  Build  │  │  │
│   │  │   code   │  │   code   │  │   YAML   │  │  files  │  │  │
│   │  └──────────┘  └──────────┘  └──────────┘  └─────────┘  │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2. Design Principles

```
┌─────────────────────────────────────────────────────────────────┐
│  SEPARATION OF CONCERNS                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  • Core Logic (onnx_codegen/core/)                             │
│    - Independent of GUI or CLI                           │
│    - Can be used as a library                                   │
│    - Unit testable                                             │
│                                                                 │
│  • CLI (onnx_codegen/cli/)                                     │
│    - Thin wrapper around Core                                   │
│    - For automation, scripting                            │
│                                                                 │
│  • GUI (onnx_codegen/gui/)                                     │
│    - Thin wrapper around Core                                   │
│    - For interactive use                                  │
│    - Only depends on PySide6                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3. Project Structure

```
onnx_codegen/
├── __init__.py
├── __main__.py              # Entry point
│
├── core/                    # Core logic (no GUI dependencies)
│   ├── __init__.py
│   ├── analyzer.py          # ONNX analysis
│   ├── detector.py          # Architecture detection
│   ├── parser.py            # Python code parser
│   ├── translator.py        # Python to C++ translator
│   ├── config.py            # Config schema & builder
│   ├── generator.py         # Code generation
│   └── templates/           # Code templates
│       ├── yolo.py
│       ├── detr.py
│       ├── ssd.py
│       └── end_to_end.py
│
├── cli/                     # CLI interface
│   ├── __init__.py
│   └── main.py
│
├── gui/                     # PySide6 GUI
│   ├── __init__.py
│   ├── main.py              # Application entry
│   ├── main_window.py       # Main window
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── file_picker.py
│   │   ├── analysis_view.py
│   │   ├── config_editor.py
│   │   ├── code_preview.py
│   │   └── progress_dialog.py
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── analyze_worker.py
│   │   └── generate_worker.py
│   └── resources/
│       ├── icons/
│       └── styles/
│
└── tests/
    ├── test_analyzer.py
    ├── test_detector.py
    ├── test_generator.py
    └── test_gui.py
```

---

## 2. Two operating modes

### 2.1. Mode A: ONNX + Python code (Recommended)

```
Input:  model.onnx + inference.py
Output: C++ code only (translated from Python)

Confidence: 95%+
```

**Workflow:**
```
Python code ──→ AST Parser ──→ Extract logic ──→ Translate to C++
                                    │
ONNX file ──→ Analyzer ──→ Validate & supplement info
```

**Note:** When user provides Python code, tool does NOT generate new Python code, only translates to C++.

### 2.2. Mode B: ONNX only

```
Input:  model.onnx
Output: C++ code + Python code (to verify)

Confidence: 70-85% (depends on model)
```

**Workflow:**
```
ONNX file ──→ Analyzer ──→ Detect architecture ──→ User confirm
                                                        │
                          Generate from template ◄──────┘
```

**Note:** When no Python code, tool generates both Python (to verify) and C++ (for deployment).

### 2.3. Dependencies & Environment

Tool requires the following dependencies for full functionality:

```
┌─────────────────────────────────────────────────────────────────┐
│  TOOL DEPENDENCIES                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  REQUIRED (required to verify C++ code):                       │
│  ────────────────────────────────────────                       │
│  Python:                                                        │
│  • Python >= 3.9                                               │
│  • onnx >= 1.14.0                                              │
│  • onnxruntime >= 1.16.0                                       │
│  • numpy >= 1.24.0                                             │
│  • PySide6 >= 6.5.0                                            │
│  • PyYAML >= 6.0                                               │
│  • Pillow >= 10.0.0                                            │
│                                                                 │
│  C++ Build Tools:                                               │
│  • CMake >= 3.18                                               │
│  • C++ compiler (gcc/clang/msvc)                              │
│  • ONNX Runtime C++ libraries                                  │
│  • OpenCV C++ libraries        ← REQUIRED cho verify          │
│                                                                 │
│  OPTIONAL (for mobile targets):                                │
│  ─────────────────────────────                                  │
│  • Android NDK        → generate/verify Android code          │
│  • Android Emulator   → run Android code on PC              │
│  • Xcode (macOS only) → generate/verify iOS code              │
│                                                                 │
│  PLATFORM NOTES:                                                │
│  • Windows/Linux: can generate + verify C++ and Android           │
│  • Windows/Linux: can generate iOS but CANNOT verify      │
│  • macOS: can generate + verify all platforms                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**CLI check environment:**
```bash
onnx-codegen --check-env
```

**Startup behavior:**
- Tool checks all dependencies on startup
- Missing required → Error + install instructions
- Missing optional → Still runs, disable/warning corresponding targets

---

## 3. Module 1: ONNX Analyzer

### 3.1. Information extracted (100% accurate)

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum, auto
import onnx
import onnxruntime as ort
import numpy as np


@dataclass
class TensorInfo:
    """Information about a tensor."""
    name: str
    shape: List[int]
    dtype: str
    is_dynamic: bool = False  # True if available dimension is -1 or symbolic


@dataclass 
class ONNXModelInfo:
    """Information extracted from ONNX file."""
    # Guaranteed correct
    inputs: List[TensorInfo]
    outputs: List[TensorInfo]
    opset_version: int
    ir_version: int
    
    # Metadata (may be empty)
    producer_name: str = ""
    producer_version: str = ""
    model_version: int = 0
    doc_string: str = ""
    custom_metadata: Dict[str, str] = field(default_factory=dict)
    
    # Graph analysis
    operators: List[str] = field(default_factory=list)
    num_nodes: int = 0
    has_dynamic_shape: bool = False
    
    # File info
    file_path: str = ""
    file_size_mb: float = 0.0


class ONNXAnalyzer:
    """Analyze ONNX file to extract information."""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self._onnx_model = None
        self._session = None
    
    @property
    def onnx_model(self):
        """Lazy load ONNX model."""
        if self._onnx_model is None:
            self._onnx_model = onnx.load(self.model_path)
        return self._onnx_model
    
    @property
    def session(self):
        """Lazy load ONNX Runtime session."""
        if self._session is None:
            self._session = ort.InferenceSession(self.model_path)
        return self._session
    
    def analyze(self, progress_callback=None) -> ONNXModelInfo:
        """
        Comprehensive analysis of ONNX model.
        
        Args:
            progress_callback: Optional callback for progress reporting
        """
        if progress_callback:
            progress_callback(10, "Loading model...")
        
        # File info
        import os
        file_size = os.path.getsize(self.model_path) / (1024 * 1024)
        
        if progress_callback:
            progress_callback(30, "Analyzing inputs/outputs...")
        
        # Input info
        inputs = []
        for inp in self.session.get_inputs():
            shape = list(inp.shape)
            is_dynamic = any(isinstance(d, str) or d is None or d == -1 for d in shape)
            inputs.append(TensorInfo(
                name=inp.name,
                shape=shape,
                dtype=inp.type,
                is_dynamic=is_dynamic
            ))
        
        # Output info
        outputs = []
        for out in self.session.get_outputs():
            shape = list(out.shape)
            is_dynamic = any(isinstance(d, str) or d is None or d == -1 for d in shape)
            outputs.append(TensorInfo(
                name=out.name,
                shape=shape,
                dtype=out.type,
                is_dynamic=is_dynamic
            ))
        
        if progress_callback:
            progress_callback(60, "Extracting metadata...")
        
        # Metadata
        model = self.onnx_model
        custom_metadata = {}
        for prop in model.metadata_props:
            custom_metadata[prop.key] = prop.value
        
        if progress_callback:
            progress_callback(80, "Analyzing graph operators...")
        
        # Graph analysis
        operators = list(set(node.op_type for node in model.graph.node))
        
        if progress_callback:
            progress_callback(100, "Done")
        
        return ONNXModelInfo(
            inputs=inputs,
            outputs=outputs,
            opset_version=model.opset_import[0].version if model.opset_import else 0,
            ir_version=model.ir_version,
            producer_name=model.producer_name,
            producer_version=model.producer_version,
            model_version=model.model_version,
            doc_string=model.doc_string,
            custom_metadata=custom_metadata,
            operators=operators,
            num_nodes=len(model.graph.node),
            has_dynamic_shape=any(i.is_dynamic for i in inputs),
            file_path=self.model_path,
            file_size_mb=file_size
        )
    
    def run_inference(self, input_data: Dict[str, np.ndarray]) -> List[np.ndarray]:
        """Run inference for testing."""
        output_names = [o.name for o in self.session.get_outputs()]
        return self.session.run(output_names, input_data)
```

### 3.2. Architecture Detection (Mode B - Heuristic)

```python
class Architecture(Enum):
    YOLOV5 = auto()
    YOLOV8 = auto()
    YOLOV11 = auto()
    DETR = auto()
    SSD = auto()
    EFFICIENTDET = auto()
    END_TO_END = auto()  # Model already has NMS
    CLASSIFIER = auto()   # Classification model
    UNKNOWN = auto()


@dataclass
class DetectionResult:
    """Results nhận diện architecture."""
    architecture: Architecture
    confidence: float  # 0.0 - 1.0
    evidence: List[str]  # Reason for conclusion
    suggestions: Dict[str, Any]  # Suggestions config


class ArchitectureDetector:
    """Detect architecture từ ONNX model."""
    
    # Patterns for each architecture
    PATTERNS = {
        Architecture.YOLOV8: {
            "output_patterns": [
                lambda shapes: len(shapes) == 1 and len(shapes[0]) == 3 
                              and shapes[0][2] in [8400, 6300, 5040, 20160, 25200],
            ],
            "op_patterns": ["Conv", "SiLU", "Concat", "Split"],
            "metadata_keywords": ["ultralytics", "yolov8", "yolo"],
            "typical_input": [640, 640],
        },
        Architecture.YOLOV5: {
            "output_patterns": [
                lambda shapes: len(shapes) == 1 and len(shapes[0]) == 3
                              and shapes[0][1] in [25200, 20160],
            ],
            "op_patterns": ["Conv", "SiLU", "Concat"],
            "metadata_keywords": ["yolov5"],
            "typical_input": [640, 640],
        },
        Architecture.DETR: {
            "output_patterns": [
                lambda shapes: len(shapes) == 2 
                              and shapes[0][1] == shapes[1][1]
                              and shapes[1][-1] == 4,
            ],
            "op_patterns": ["MatMul", "Softmax", "LayerNormalization"],
            "metadata_keywords": ["detr", "transformer", "facebook"],
            "typical_input": [800, 800],
        },
        Architecture.SSD: {
            "output_patterns": [
                lambda shapes: len(shapes) == 2 
                              and shapes[0][1] == shapes[1][1] == 8732,
            ],
            "op_patterns": ["Conv", "Relu", "Concat"],
            "metadata_keywords": ["ssd", "mobilenet"],
            "typical_input": [300, 300],
        },
        Architecture.END_TO_END: {
            "output_patterns": [
                lambda shapes: len(shapes) == 1 and len(shapes[0]) == 3
                              and shapes[0][-1] in [6, 7],
            ],
            "op_patterns": ["NonMaxSuppression"],
            "metadata_keywords": ["end2end", "nms"],
            "typical_input": [640, 640],
        },
        Architecture.CLASSIFIER: {
            "output_patterns": [
                lambda shapes: len(shapes) == 1 and len(shapes[0]) == 2,
            ],
            "op_patterns": ["Softmax", "Gemm"],
            "metadata_keywords": ["classifier", "resnet", "efficientnet"],
            "typical_input": [224, 224],
        },
    }
    
    def __init__(self, model_info: ONNXModelInfo):
        self.info = model_info
    
    def detect(self) -> DetectionResult:
        """Detect architecture."""
        scores = {}
        evidence = {}
        
        output_shapes = [list(o.shape) for o in self.info.outputs]
        
        for arch, patterns in self.PATTERNS.items():
            score = 0.0
            arch_evidence = []
            
            # Check output patterns
            for pattern_fn in patterns["output_patterns"]:
                try:
                    if pattern_fn(output_shapes):
                        score += 0.4
                        arch_evidence.append(f"Output shape matches {arch.name} pattern")
                except:
                    pass
            
            # Check operators
            matched_ops = set(patterns["op_patterns"]) & set(self.info.operators)
            if matched_ops:
                op_score = len(matched_ops) / len(patterns["op_patterns"]) * 0.3
                score += op_score
                arch_evidence.append(f"Found operators: {matched_ops}")
            
            # Check metadata
            metadata_str = f"{self.info.producer_name} {self.info.doc_string}".lower()
            for keyword in patterns["metadata_keywords"]:
                if keyword in metadata_str:
                    score += 0.2
                    arch_evidence.append(f"Metadata contains '{keyword}'")
                    break
            
            # Check input size
            if self.info.inputs:
                input_shape = self.info.inputs[0].shape
                if len(input_shape) == 4:
                    h, w = input_shape[2], input_shape[3]
                    typical = patterns["typical_input"]
                    if h == typical[0] and w == typical[1]:
                        score += 0.1
                        arch_evidence.append(f"Input size matches typical {arch.name}")
            
            scores[arch] = min(score, 1.0)
            evidence[arch] = arch_evidence
        
        # Select architecture with highest score
        best_arch = max(scores, key=scores.get)
        best_score = scores[best_arch]
        
        if best_score < 0.3:
            best_arch = Architecture.UNKNOWN
        
        # Create suggestions
        suggestions = self._create_suggestions(best_arch, output_shapes)
        
        return DetectionResult(
            architecture=best_arch,
            confidence=best_score,
            evidence=evidence.get(best_arch, []),
            suggestions=suggestions
        )
    
    def _create_suggestions(self, arch: Architecture, output_shapes: List) -> Dict:
        """Create config suggestions based on architecture."""
        suggestions = {
            "preprocessing": {
                "color_format": "RGB",
                "normalize": True,
                "scale": 1.0 / 255.0,
                "mean": [0.0, 0.0, 0.0],
                "std": [1.0, 1.0, 1.0],
                "resize_mode": "letterbox",
            },
            "postprocessing": {
                "conf_threshold": 0.25,
                "iou_threshold": 0.45,
            }
        }
        
        if arch in [Architecture.YOLOV5, Architecture.YOLOV8, Architecture.YOLOV11]:
            if output_shapes and len(output_shapes[0]) == 3:
                num_features = output_shapes[0][1]
                suggestions["num_classes"] = num_features - 4
            suggestions["postprocessing"]["type"] = "nms"
            
        elif arch == Architecture.DETR:
            suggestions["preprocessing"]["mean"] = [0.485, 0.456, 0.406]
            suggestions["preprocessing"]["std"] = [0.229, 0.224, 0.225]
            suggestions["preprocessing"]["resize_mode"] = "resize"
            suggestions["postprocessing"]["type"] = "threshold"
            suggestions["postprocessing"]["conf_threshold"] = 0.7
            
        elif arch == Architecture.SSD:
            suggestions["preprocessing"]["mean"] = [123.0, 117.0, 104.0]
            suggestions["preprocessing"]["scale"] = 1.0
            suggestions["preprocessing"]["normalize"] = False
            suggestions["postprocessing"]["type"] = "anchor_decode_nms"
            
        elif arch == Architecture.END_TO_END:
            suggestions["postprocessing"]["type"] = "direct_read"
            
        elif arch == Architecture.CLASSIFIER:
            suggestions["postprocessing"]["type"] = "softmax"
            suggestions["preprocessing"]["resize_mode"] = "resize"
        
        return suggestions
```

### 3.3. Python Code Parser

Parser to extract preprocessing/postprocessing config from Python inference code.

```python
# core/python_parser.py

import ast
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


@dataclass
class ParsedPreprocessing:
    """Preprocessing information extracted from Python code."""
    input_size: Optional[Tuple[int, int]] = None  # (height, width)
    color_format: Optional[str] = None  # "RGB", "BGR"
    resize_mode: Optional[str] = None  # "resize", "letterbox"
    normalize: Optional[bool] = None
    scale: Optional[float] = None  # e.g., 1/255 = 0.00392156862745098
    mean: Optional[Tuple[float, float, float]] = None
    std: Optional[Tuple[float, float, float]] = None
    channel_order: Optional[str] = None  # "CHW", "HWC"
    
    # Evidence (code lines found)
    evidence: Dict[str, str] = field(default_factory=dict)


@dataclass
class ParsedPostprocessing:
    """Postprocessing information extracted from Python code."""
    conf_threshold: Optional[float] = None
    iou_threshold: Optional[float] = None
    max_detections: Optional[int] = None
    num_classes: Optional[int] = None
    has_nms: bool = False
    output_format: Optional[str] = None  # "xyxy", "xywh", "cxcywh"
    
    # Evidence
    evidence: Dict[str, str] = field(default_factory=dict)


@dataclass
class ParseResult:
    """Results parse Python code."""
    success: bool
    preprocessing: ParsedPreprocessing
    postprocessing: ParsedPostprocessing
    model_path_in_code: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class PythonCodeParser:
    """
    Parser to extract preprocessing/postprocessing from Python inference code.
    
    Supports common patterns:
    - OpenCV: cv2.imread, cv2.resize, cv2.cvtColor
    - PIL: Image.open, image.resize
    - NumPy: np.array, transpose, normalize
    - Ultralytics YOLO patterns
    - Custom preprocessing functions
    """
    
    # Patterns to detect preprocessing
    PREPROCESS_PATTERNS = {
        # Resize patterns
        "resize_cv2": re.compile(r"cv2\.resize\s*\(\s*\w+\s*,\s*\((\d+)\s*,\s*(\d+)\)"),
        "resize_pil": re.compile(r"\.resize\s*\(\s*\((\d+)\s*,\s*(\d+)\)"),
        "letterbox": re.compile(r"letterbox|LetterBox|letter_box"),
        
        # Color conversion
        "bgr2rgb": re.compile(r"cv2\.COLOR_BGR2RGB|cvtColor.*BGR2RGB|\[:,\s*:,\s*::-1\]"),
        "rgb2bgr": re.compile(r"cv2\.COLOR_RGB2BGR|cvtColor.*RGB2BGR"),
        
        # Normalize patterns
        "div_255": re.compile(r"/\s*255\.?0?|/255|astype.*float.*255|\*\s*\(1\s*/\s*255"),
        "normalize_mean_std": re.compile(r"mean\s*=|std\s*=|normalize\s*\("),
        
        # Transpose patterns
        "transpose_chw": re.compile(r"transpose\s*\(\s*\(?2\s*,\s*0\s*,\s*1|transpose\s*\(\s*0\s*,\s*3\s*,\s*1\s*,\s*2"),
        "permute_chw": re.compile(r"permute\s*\(\s*\(?2\s*,\s*0\s*,\s*1|permute\s*\(\s*0\s*,\s*3\s*,\s*1\s*,\s*2"),
        
        # Input size from shape
        "input_shape": re.compile(r"input_shape\s*=\s*\[?\(?\s*\d+\s*,\s*(\d+)\s*,\s*(\d+)"),
        "img_size": re.compile(r"img_size\s*=\s*(\d+)|imgsz\s*=\s*(\d+)|input_size\s*=\s*(\d+)"),
    }
    
    # Patterns to detect postprocessing
    POSTPROCESS_PATTERNS = {
        # NMS patterns
        "nms_cv2": re.compile(r"cv2\.dnn\.NMSBoxes"),
        "nms_torchvision": re.compile(r"torchvision\.ops\.nms|ops\.nms"),
        "nms_custom": re.compile(r"def\s+nms|non_max_suppression|NonMaxSuppression"),
        
        # Threshold patterns
        "conf_threshold": re.compile(r"conf(?:_thresh(?:old)?|idence)?\s*[=:>]\s*(0?\.\d+)"),
        "iou_threshold": re.compile(r"iou(?:_thresh(?:old)?|_thres)?\s*[=:>]\s*(0?\.\d+)"),
        "score_threshold": re.compile(r"score(?:_thresh(?:old)?|_thres)?\s*[=:>]\s*(0?\.\d+)"),
        
        # Box format patterns
        "xyxy": re.compile(r"xyxy|x1y1x2y2|boxes\[:,\s*:4\]"),
        "xywh": re.compile(r"xywh(?!2)|boxes\[:,\s*:4\].*width.*height"),
        "cxcywh": re.compile(r"cxcywh|center_x|cx\s*,\s*cy"),
        
        # Classes
        "num_classes": re.compile(r"num_classes\s*=\s*(\d+)|n_classes\s*=\s*(\d+)|classes\s*=\s*(\d+)"),
        "max_det": re.compile(r"max_det\s*=\s*(\d+)|max_detections\s*=\s*(\d+)"),
    }
    
    # Common mean/std values
    KNOWN_NORMALIZATIONS = {
        "imagenet": {
            "mean": (0.485, 0.456, 0.406),
            "std": (0.229, 0.224, 0.225)
        },
        "yolo": {
            "mean": (0.0, 0.0, 0.0),
            "std": (1.0, 1.0, 1.0)
        }
    }
    
    def __init__(self, code_path: str):
        self.code_path = Path(code_path)
        self.code_content = ""
        self.ast_tree = None
        
    def parse(self) -> ParseResult:
        """Parse Python code and extract config."""
        preprocessing = ParsedPreprocessing()
        postprocessing = ParsedPostprocessing()
        errors = []
        warnings = []
        model_path = None
        
        try:
            # Read file
            self.code_content = self.code_path.read_text(encoding='utf-8')
            
            # Try to parse AST
            try:
                self.ast_tree = ast.parse(self.code_content)
            except SyntaxError as e:
                warnings.append(f"AST parse failed: {e}. Using regex only.")
            
            # Extract preprocessing
            preprocessing = self._extract_preprocessing()
            
            # Extract postprocessing
            postprocessing = self._extract_postprocessing()
            
            # Extract model path if present
            model_path = self._extract_model_path()
            
            # Validate and fill gaps
            self._validate_and_fill(preprocessing, postprocessing, warnings)
            
            return ParseResult(
                success=True,
                preprocessing=preprocessing,
                postprocessing=postprocessing,
                model_path_in_code=model_path,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            errors.append(f"Parse error: {str(e)}")
            return ParseResult(
                success=False,
                preprocessing=preprocessing,
                postprocessing=postprocessing,
                errors=errors,
                warnings=warnings
            )
    
    def _extract_preprocessing(self) -> ParsedPreprocessing:
        """Extract preprocessing config."""
        result = ParsedPreprocessing()
        
        # Extract input size
        for pattern_name in ["resize_cv2", "resize_pil"]:
            match = self.PREPROCESS_PATTERNS[pattern_name].search(self.code_content)
            if match:
                w, h = int(match.group(1)), int(match.group(2))
                result.input_size = (h, w)  # height, width
                result.evidence["input_size"] = match.group(0)
                break
        
        # Check for img_size = 640 style
        if result.input_size is None:
            match = self.PREPROCESS_PATTERNS["img_size"].search(self.code_content)
            if match:
                size = int(match.group(1) or match.group(2) or match.group(3))
                result.input_size = (size, size)
                result.evidence["input_size"] = match.group(0)
        
        # Detect letterbox vs resize
        if self.PREPROCESS_PATTERNS["letterbox"].search(self.code_content):
            result.resize_mode = "letterbox"
            result.evidence["resize_mode"] = "letterbox pattern found"
        else:
            result.resize_mode = "resize"
        
        # Detect color format
        if self.PREPROCESS_PATTERNS["bgr2rgb"].search(self.code_content):
            result.color_format = "RGB"
            result.evidence["color_format"] = "BGR2RGB conversion found"
        elif self.PREPROCESS_PATTERNS["rgb2bgr"].search(self.code_content):
            result.color_format = "BGR"
            result.evidence["color_format"] = "RGB2BGR conversion found"
        elif "cv2.imread" in self.code_content and "cvtColor" not in self.code_content:
            result.color_format = "BGR"
            result.evidence["color_format"] = "cv2.imread without conversion = BGR"
        else:
            result.color_format = "RGB"  # Default assumption
        
        # Detect normalization
        if self.PREPROCESS_PATTERNS["div_255"].search(self.code_content):
            result.normalize = True
            result.scale = 1.0 / 255.0
            result.evidence["normalize"] = "/255 normalization found"
        
        # Detect mean/std normalization
        mean_match = re.search(r"mean\s*=\s*\[?\(?([\d.,\s]+)\]?\)?", self.code_content)
        std_match = re.search(r"std\s*=\s*\[?\(?([\d.,\s]+)\]?\)?", self.code_content)
        
        if mean_match:
            try:
                values = [float(x.strip()) for x in mean_match.group(1).split(",")]
                if len(values) == 3:
                    result.mean = tuple(values)
                    result.evidence["mean"] = mean_match.group(0)
            except:
                pass
        
        if std_match:
            try:
                values = [float(x.strip()) for x in std_match.group(1).split(",")]
                if len(values) == 3:
                    result.std = tuple(values)
                    result.evidence["std"] = std_match.group(0)
            except:
                pass
        
        # Detect channel order
        if (self.PREPROCESS_PATTERNS["transpose_chw"].search(self.code_content) or
            self.PREPROCESS_PATTERNS["permute_chw"].search(self.code_content)):
            result.channel_order = "CHW"
            result.evidence["channel_order"] = "transpose to CHW found"
        else:
            result.channel_order = "CHW"  # ONNX default
        
        return result
    
    def _extract_postprocessing(self) -> ParsedPostprocessing:
        """Extract postprocessing config."""
        result = ParsedPostprocessing()
        
        # Detect NMS
        for pattern_name in ["nms_cv2", "nms_torchvision", "nms_custom"]:
            if self.POSTPROCESS_PATTERNS[pattern_name].search(self.code_content):
                result.has_nms = True
                result.evidence["nms"] = f"{pattern_name} found"
                break
        
        # Extract confidence threshold
        match = self.POSTPROCESS_PATTERNS["conf_threshold"].search(self.code_content)
        if match:
            result.conf_threshold = float(match.group(1))
            result.evidence["conf_threshold"] = match.group(0)
        else:
            # Try score_threshold as fallback
            match = self.POSTPROCESS_PATTERNS["score_threshold"].search(self.code_content)
            if match:
                result.conf_threshold = float(match.group(1))
                result.evidence["conf_threshold"] = match.group(0)
        
        # Extract IoU threshold
        match = self.POSTPROCESS_PATTERNS["iou_threshold"].search(self.code_content)
        if match:
            result.iou_threshold = float(match.group(1))
            result.evidence["iou_threshold"] = match.group(0)
        
        # Extract num_classes
        match = self.POSTPROCESS_PATTERNS["num_classes"].search(self.code_content)
        if match:
            value = match.group(1) or match.group(2) or match.group(3)
            result.num_classes = int(value)
            result.evidence["num_classes"] = match.group(0)
        
        # Extract max_detections
        match = self.POSTPROCESS_PATTERNS["max_det"].search(self.code_content)
        if match:
            value = match.group(1) or match.group(2)
            result.max_detections = int(value)
            result.evidence["max_detections"] = match.group(0)
        
        # Detect output format
        if self.POSTPROCESS_PATTERNS["cxcywh"].search(self.code_content):
            result.output_format = "cxcywh"
        elif self.POSTPROCESS_PATTERNS["xywh"].search(self.code_content):
            result.output_format = "xywh"
        elif self.POSTPROCESS_PATTERNS["xyxy"].search(self.code_content):
            result.output_format = "xyxy"
        
        return result
    
    def _extract_model_path(self) -> Optional[str]:
        """Extract model path from code."""
        patterns = [
            re.compile(r'["\']([^"\']+\.onnx)["\']'),
            re.compile(r'model_path\s*=\s*["\']([^"\']+)["\']'),
            re.compile(r'onnx\.load\s*\(["\']([^"\']+)["\']'),
            re.compile(r'InferenceSession\s*\(["\']([^"\']+)["\']'),
        ]
        
        for pattern in patterns:
            match = pattern.search(self.code_content)
            if match:
                return match.group(1)
        
        return None
    
    def _validate_and_fill(self, prep: ParsedPreprocessing, post: ParsedPostprocessing, 
                          warnings: List[str]):
        """Validate and fill default values for missing fields."""
        
        # Default preprocessing values
        if prep.input_size is None:
            prep.input_size = (640, 640)
            warnings.append("Input size not found, defaulting to 640x640")
        
        if prep.normalize is None:
            prep.normalize = True
            prep.scale = 1.0 / 255.0
            warnings.append("Normalization not detected, defaulting to /255")
        
        # Default postprocessing values
        if post.conf_threshold is None:
            post.conf_threshold = 0.25
            warnings.append("Confidence threshold not found, defaulting to 0.25")
        
        if post.iou_threshold is None:
            post.iou_threshold = 0.45
            warnings.append("IoU threshold not found, defaulting to 0.45")
        
        if post.num_classes is None:
            post.num_classes = 80
            warnings.append("Number of classes not found, defaulting to 80 (COCO)")


class UltralyticsParser(PythonCodeParser):
    """
    Specialized parser cho Ultralytics YOLO code.
    Knows patterns of ultralytics package.
    """
    
    ULTRALYTICS_PATTERNS = {
        "model_load": re.compile(r"YOLO\s*\(['\"]([^'\"]+)['\"]\)"),
        "predict": re.compile(r"\.predict\s*\(|\.track\s*\("),
        "conf": re.compile(r"conf\s*=\s*(0?\.\d+)"),
        "iou": re.compile(r"iou\s*=\s*(0?\.\d+)"),
        "imgsz": re.compile(r"imgsz\s*=\s*(\d+)"),
        "classes": re.compile(r"classes\s*=\s*\[([^\]]+)\]"),
    }
    
    def is_ultralytics_code(self) -> bool:
        """Check if this is Ultralytics code."""
        return "ultralytics" in self.code_content or "YOLO(" in self.code_content
    
    def parse(self) -> ParseResult:
        """Parse Ultralytics-specific code."""
        # First, read the file
        self.code_content = self.code_path.read_text(encoding='utf-8')
        
        if not self.is_ultralytics_code():
            # Fall back to generic parser
            return super().parse()
        
        preprocessing = ParsedPreprocessing()
        postprocessing = ParsedPostprocessing()
        warnings = []
        errors = []
        
        # Ultralytics defaults
        preprocessing.color_format = "RGB"
        preprocessing.resize_mode = "letterbox"
        preprocessing.normalize = True
        preprocessing.scale = 1.0 / 255.0
        preprocessing.channel_order = "CHW"
        
        postprocessing.has_nms = True
        postprocessing.output_format = "xyxy"
        
        # Extract imgsz
        match = self.ULTRALYTICS_PATTERNS["imgsz"].search(self.code_content)
        if match:
            size = int(match.group(1))
            preprocessing.input_size = (size, size)
        else:
            preprocessing.input_size = (640, 640)
            warnings.append("imgsz not specified, using default 640")
        
        # Extract conf
        match = self.ULTRALYTICS_PATTERNS["conf"].search(self.code_content)
        if match:
            postprocessing.conf_threshold = float(match.group(1))
        else:
            postprocessing.conf_threshold = 0.25
        
        # Extract iou
        match = self.ULTRALYTICS_PATTERNS["iou"].search(self.code_content)
        if match:
            postprocessing.iou_threshold = float(match.group(1))
        else:
            postprocessing.iou_threshold = 0.7  # Ultralytics default
        
        # Extract model path
        model_path = None
        match = self.ULTRALYTICS_PATTERNS["model_load"].search(self.code_content)
        if match:
            model_path = match.group(1)
        
        return ParseResult(
            success=True,
            preprocessing=preprocessing,
            postprocessing=postprocessing,
            model_path_in_code=model_path,
            errors=errors,
            warnings=warnings
        )
```

---

## 4. Module 2: Config Schema

```python
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from enum import Enum
import yaml
import json


class ResizeMode(Enum):
    RESIZE = "resize"
    LETTERBOX = "letterbox"
    CROP = "crop"


class ColorFormat(Enum):
    RGB = "rgb"
    BGR = "bgr"


class ImageInputMode(Enum):
    """Image input reading mode."""
    OPENCV = "opencv"              # cv::Mat based (default, full features)
    RAW_BUFFER = "raw_buffer"      # uint8_t* RGB/BGR pointer
    ANDROID_NATIVE = "android"     # JNI + AndroidBitmap
    IOS_NATIVE = "ios"             # CVPixelBufferRef
    STB_IMAGE = "stb_image"        # Lightweight, header-only


class PostprocessType(Enum):
    NMS = "nms"
    SOFT_NMS = "soft_nms"
    THRESHOLD = "threshold"
    ANCHOR_DECODE_NMS = "anchor_nms"
    DIRECT_READ = "direct"
    SOFTMAX = "softmax"


@dataclass
class PreprocessConfig:
    """Preprocessing configuration."""
    input_width: int = 640
    input_height: int = 640
    color_format: ColorFormat = ColorFormat.RGB
    resize_mode: ResizeMode = ResizeMode.LETTERBOX
    image_input_mode: ImageInputMode = ImageInputMode.OPENCV  # NEW
    normalize: bool = True
    scale: float = 1.0 / 255.0
    mean: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    std: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    padding_value: int = 114


@dataclass
class PostprocessConfig:
    """Postprocessing configuration."""
    type: PostprocessType = PostprocessType.NMS
    conf_threshold: float = 0.25
    iou_threshold: float = 0.45
    max_detections: int = 300
    num_classes: int = 80


@dataclass
class ModelConfig:
    """Complete model configuration."""
    # Model info
    model_path: str = ""
    architecture: str = "unknown"
    
    # I/O info (from ONNX)
    input_name: str = "images"
    input_shape: List[int] = field(default_factory=lambda: [1, 3, 640, 640])
    output_names: List[str] = field(default_factory=list)
    output_shapes: List[List[int]] = field(default_factory=list)
    
    # Processing configs
    preprocess: PreprocessConfig = field(default_factory=PreprocessConfig)
    postprocess: PostprocessConfig = field(default_factory=PostprocessConfig)
    
    # Class labels
    class_names: List[str] = field(default_factory=list)
    
    # Generation options
    target_language: str = "cpp"
    target_platform: str = "android"
    
    # Metadata
    confidence_score: float = 0.0
    source: str = "unknown"
    warnings: List[str] = field(default_factory=list)
    
    def to_yaml(self, path: str):
        """Save config to YAML file."""
        data = self._to_serializable_dict()
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def to_json(self, path: str):
        """Save config to JSON file."""
        data = self._to_serializable_dict()
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _to_serializable_dict(self) -> dict:
        """Convert to serializable dict (handle Enums)."""
        data = asdict(self)
        data['preprocess']['color_format'] = self.preprocess.color_format.value
        data['preprocess']['resize_mode'] = self.preprocess.resize_mode.value
        data['postprocess']['type'] = self.postprocess.type.value
        return data
    
    @classmethod
    def from_yaml(cls, path: str) -> 'ModelConfig':
        """Load config from YAML file."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls._from_dict(data)
    
    @classmethod
    def _from_dict(cls, data: dict) -> 'ModelConfig':
        """Create config from dict."""
        if 'preprocess' in data:
            pre = data['preprocess']
            pre['color_format'] = ColorFormat(pre.get('color_format', 'rgb'))
            pre['resize_mode'] = ResizeMode(pre.get('resize_mode', 'letterbox'))
            data['preprocess'] = PreprocessConfig(**pre)
        
        if 'postprocess' in data:
            post = data['postprocess']
            post['type'] = PostprocessType(post.get('type', 'nms'))
            data['postprocess'] = PostprocessConfig(**post)
        
        return cls(**data)
```

### 4.2. Config Builder

Config Builder combines information from ONNX Analyzer and Python Parser to create ModelConfig.

```python
# core/config_builder.py

from typing import Optional, Tuple
from dataclasses import dataclass, field
from .analyzer import ONNXModelInfo, ArchitectureDetector, Architecture, DetectionResult
from .python_parser import ParseResult, ParsedPreprocessing, ParsedPostprocessing
from .config import (
    ModelConfig, PreprocessConfig, PostprocessConfig,
    ResizeMode, ColorFormat, PostprocessType, ImageInputMode
)


@dataclass
class BuildResult:
    """Config build result."""
    config: ModelConfig
    confidence: float  # 0.0 - 1.0
    source: str  # "python_code", "onnx_heuristic", "user_manual"
    warnings: List[str] = field(default_factory=list)
    evidence: Dict[str, str] = field(default_factory=dict)


class ConfigBuilder:
    """
    Builder to create ModelConfig from multiple sources.
    
    Priority order:
    1. Python code (if available) - highest confidence
    2. ONNX metadata + heuristics - medium confidence
    3. Default values - lowest confidence
    """
    
    def __init__(self, onnx_info: ONNXModelInfo, parse_result: Optional[ParseResult] = None):
        self.onnx_info = onnx_info
        self.parse_result = parse_result
        self.warnings = []
        self.evidence = {}
    
    def build(self) -> BuildResult:
        """Build ModelConfig from available sources."""
        
        if self.parse_result and self.parse_result.success:
            # Mode A: ONNX + Python code
            return self._build_from_python()
        else:
            # Mode B: ONNX only (heuristic)
            return self._build_from_heuristic()
    
    def _build_from_python(self) -> BuildResult:
        """Build config from parsed Python code."""
        prep = self.parse_result.preprocessing
        post = self.parse_result.postprocessing
        
        # Build PreprocessConfig
        preprocess = PreprocessConfig(
            input_width=prep.input_size[1] if prep.input_size else 640,
            input_height=prep.input_size[0] if prep.input_size else 640,
            color_format=ColorFormat(prep.color_format.lower()) if prep.color_format else ColorFormat.RGB,
            resize_mode=ResizeMode(prep.resize_mode) if prep.resize_mode else ResizeMode.LETTERBOX,
            normalize=prep.normalize if prep.normalize is not None else True,
            scale=prep.scale if prep.scale else 1.0/255.0,
            mean=list(prep.mean) if prep.mean else [0.0, 0.0, 0.0],
            std=list(prep.std) if prep.std else [1.0, 1.0, 1.0],
        )
        
        # Build PostprocessConfig
        postprocess = PostprocessConfig(
            type=PostprocessType.NMS if post.has_nms else PostprocessType.THRESHOLD,
            confidence_threshold=post.conf_threshold if post.conf_threshold else 0.25,
            iou_threshold=post.iou_threshold if post.iou_threshold else 0.45,
            max_detections=post.max_detections if post.max_detections else 300,
            num_classes=post.num_classes if post.num_classes else self._infer_num_classes(),
        )
        
        # Build ModelConfig
        config = ModelConfig(
            model_path=self.onnx_info.file_path,
            input_name=self.onnx_info.inputs[0].name if self.onnx_info.inputs else "images",
            output_names=[o.name for o in self.onnx_info.outputs],
            preprocess=preprocess,
            postprocess=postprocess,
            confidence_score=0.9,  # High confidence from Python code
            source="python_code",
            warnings=self.parse_result.warnings,
        )
        
        # Collect evidence
        self.evidence.update(prep.evidence)
        self.evidence.update(post.evidence)
        
        return BuildResult(
            config=config,
            confidence=0.9,
            source="python_code",
            warnings=self.parse_result.warnings,
            evidence=self.evidence
        )
    
    def _build_from_heuristic(self) -> BuildResult:
        """Build config from ONNX heuristics."""
        
        # Detect architecture
        detector = ArchitectureDetector(self.onnx_info)
        detection = detector.detect()
        
        # Get suggestions from detector
        suggestions = detection.suggestions
        
        # Build PreprocessConfig từ suggestions
        prep_suggest = suggestions.get("preprocessing", {})
        preprocess = PreprocessConfig(
            input_width=self._get_input_width(),
            input_height=self._get_input_height(),
            color_format=ColorFormat(prep_suggest.get("color_format", "rgb")),
            resize_mode=ResizeMode(prep_suggest.get("resize_mode", "letterbox")),
            normalize=prep_suggest.get("normalize", True),
            scale=prep_suggest.get("scale", 1.0/255.0),
        )
        
        # Build PostprocessConfig từ suggestions
        post_suggest = suggestions.get("postprocessing", {})
        postprocess = PostprocessConfig(
            type=PostprocessType(post_suggest.get("type", "nms")),
            confidence_threshold=post_suggest.get("confidence_threshold", 0.25),
            iou_threshold=post_suggest.get("iou_threshold", 0.45),
            num_classes=self._infer_num_classes(),
        )
        
        # Build ModelConfig
        config = ModelConfig(
            model_path=self.onnx_info.file_path,
            input_name=self.onnx_info.inputs[0].name if self.onnx_info.inputs else "images",
            output_names=[o.name for o in self.onnx_info.outputs],
            preprocess=preprocess,
            postprocess=postprocess,
            confidence_score=detection.confidence,
            source="onnx_heuristic",
            warnings=self.warnings,
        )
        
        # Evidence
        self.evidence["architecture"] = f"{detection.architecture.name} (confidence: {detection.confidence:.2f})"
        self.evidence["detection_evidence"] = str(detection.evidence)
        
        return BuildResult(
            config=config,
            confidence=detection.confidence,
            source="onnx_heuristic",
            warnings=self.warnings,
            evidence=self.evidence
        )
    
    def _get_input_width(self) -> int:
        """Get input width từ ONNX model."""
        if self.onnx_info.inputs:
            shape = self.onnx_info.inputs[0].shape
            if len(shape) == 4:
                # NCHW or NHWC
                if shape[1] in [1, 3]:  # NCHW
                    return shape[3] if isinstance(shape[3], int) and shape[3] > 0 else 640
                else:  # NHWC
                    return shape[2] if isinstance(shape[2], int) and shape[2] > 0 else 640
        return 640
    
    def _get_input_height(self) -> int:
        """Get input height từ ONNX model."""
        if self.onnx_info.inputs:
            shape = self.onnx_info.inputs[0].shape
            if len(shape) == 4:
                # NCHW or NHWC
                if shape[1] in [1, 3]:  # NCHW
                    return shape[2] if isinstance(shape[2], int) and shape[2] > 0 else 640
                else:  # NHWC
                    return shape[1] if isinstance(shape[1], int) and shape[1] > 0 else 640
        return 640
    
    def _infer_num_classes(self) -> int:
        """Infer number of classes từ output shape."""
        if not self.onnx_info.outputs:
            return 80  # Default COCO
        
        output = self.onnx_info.outputs[0]
        shape = output.shape
        
        # YOLOv8: [1, 84, 8400] → 84 - 4 = 80 classes
        # YOLOv5: [1, 25200, 85] → 85 - 5 = 80 classes
        
        if len(shape) == 3:
            if shape[1] < shape[2]:  # [1, 84, 8400]
                return max(1, shape[1] - 4)
            else:  # [1, 25200, 85]
                return max(1, shape[2] - 5)
        
        return 80  # Default
    
    def override(self, **kwargs) -> 'ConfigBuilder':
        """
        Override specific config values.
        
        Example:
            builder.override(
                preprocess__input_width=416,
                postprocess__confidence_threshold=0.5
            )
        """
        # Store overrides for later application
        self._overrides = kwargs
        return self
    
    def apply_overrides(self, config: ModelConfig) -> ModelConfig:
        """Apply stored overrides to config."""
        if not hasattr(self, '_overrides'):
            return config
        
        for key, value in self._overrides.items():
            if '__' in key:
                section, field = key.split('__', 1)
                if section == 'preprocess' and hasattr(config.preprocess, field):
                    setattr(config.preprocess, field, value)
                elif section == 'postprocess' and hasattr(config.postprocess, field):
                    setattr(config.postprocess, field, value)
            elif hasattr(config, key):
                setattr(config, key, value)
        
        return config
```

---

## 5. UI/UX Design Principles

### 5.1. Core Design Principles

```
┌─────────────────────────────────────────────────────────────────┐
│  UI/UX DESIGN PRINCIPLES                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  This app follows these design principles to ensure   │
│  the best user experience.                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.1.1. Progressive Disclosure (Tiết lộ dần dần)

```
┌─────────────────────────────────────────────────────────────────┐
│  PRINCIPLES: Only show what is necessary at that moment      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ❌ WRONG: Show all 50 options at once                       │
│     → User overwhelmed, does not know where to start              │
│                                                                 │
│  ✅ CORRECT: Show step by step, expand when needed                      │
│     → User focuses on current task                         │
│                                                                 │
│  ÁP DỤNG:                                                       │
│  • Required inputs (ONNX file) shown first, clearly             │
│  • Optional inputs (Python code, Labels) ẩn trong collapsible  │
│  • Advanced settings hidden, shown when user needs                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.1.2. Two-Phase Wizard Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│  PRINCIPLES: Separate C++ Core and Mobile Wrapper                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE 1: C++ Core (Required)                                  │
│  ─────────────────────────────                                  │
│  Step 1: INPUT      → ONNX file, Python code (optional)        │
│  Step 2: CONFIGURE  → Preprocessing, postprocessing settings   │
│  Step 3: VERIFY     → Test on PC, ensure logic is correct        │
│  Step 4: GENERATE   → Generate C++ core code                       │
│                                                                 │
│  → User can STOP here if only need PC                      │
│                                                                 │
│  PHASE 2: Mobile Wrapper (Optional)                            │
│  ──────────────────────────────────                             │
│  Step 5: MOBILE CONFIG  → Select platform, use case              │
│  Step 6: GENERATE       → Sinh JNI/Swift wrapper + app code    │
│                                                                 │
│  LÝ DO TÁCH 2 PHASE:                                           │
│  • C++ core is the FOUNDATION for both PC and Mobile                   │
│  • Verify C++ on PC first → ensure logic is correct              │
│  • Mobile code is just WRAPPER, no need to re-verify logic     │
│  • Clear: C++ = logic, Mobile = integration                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.1.3. Sensible Defaults (Default hợp lý)

```
┌─────────────────────────────────────────────────────────────────┐
│  PRINCIPLES: App must work well with default config       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  QUICK PATH (80% users):                                       │
│  User only needs: Select ONNX file → Click Generate                 │
│  App tự động: Detect architecture → Set defaults → Generate code   │
│                                                                 │
│  ADVANCED PATH (20% users):                                    │
│  User can: Override any setting                      │
│  App supports: Verify before generate                         │
│                                                                 │
│  ÁP DỤNG:                                                       │
│  • Auto-detect input size từ ONNX                              │
│  • Auto-detect architecture (YOLOv8, DETR, etc.)               │
│  • Pre-fill postprocessing config based on architecture        │
│  • "Skip to Generate" button for power users                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.1.4. Immediate Feedback (Immediate Feedback)

```
┌─────────────────────────────────────────────────────────────────┐
│  PRINCIPLES: User must see action results immediately           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ÁP DỤNG:                                                       │
│  • Select ONNX → Immediately show model info                   │
│    (architecture, input shape, output shape, file size)        │
│                                                                 │
│  • Đổi config → Ngay lập tức validate                          │
│    (warning if value is invalid)                          │
│                                                                 │
│  • Run verify → Show progress bar + timing + results          │
│    (user does not have to guess what app is doing)                      │
│                                                                 │
│  • Generate code → Preview ngay trong app                      │
│    (no need to open folder to view)                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.1.5. Reversible Actions (Reversible Actions)

```
┌─────────────────────────────────────────────────────────────────┐
│  PRINCIPLES: User not afraid to try because can always go back        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ÁP DỤNG:                                                       │
│  • Back button to return to previous step                         │
│  • Reset to defaults for each section                          │
│  • Verify "Wrong" → go back to Configure, keep values       │
│  • Config history for restore (nice to have)                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.1.6. Error Prevention (Error Prevention)

```
┌─────────────────────────────────────────────────────────────────┐
│  PRINCIPLES: Preventing errors is better than fixing them                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ÁP DỤNG:                                                       │
│  • Disable "Next" button if insufficient required input           │
│  • Validate input ngay khi user nhập                           │
│  • Warning dialog if config seems invalid               │
│  • Confirm dialog before overwriting existing files          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2. User Flows

#### 5.2.1. Two main flows

```
┌─────────────────────────────────────────────────────────────────┐
│  USER FLOW A: Quick Generate (80% users)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  "I have ONNX file, want to generate C++ code for PC"                │
│                                                                 │
│  1. Select ONNX file                                             │
│  2. [Auto-detect] → Review detected config                     │
│  3. Click "Skip to Generate" hoặc Next → Next → Generate       │
│  4. Done! C++ code generated                                   │
│                                                                 │
│  Time: < 1 minute                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  USER FLOW B: Verified C++ + Mobile (20% users)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  "I want code to run correctly on PC, then generate mobile code"  │
│                                                                 │
│  PHASE 1: C++ Core                                             │
│  1. Select ONNX file                                             │
│  2. [Optional] Add Python inference code, Labels file         │
│  3. Adjust config if needed                                  │
│  4. Import test image → Run verify → View results              │
│  5. Results wrong? → Adjust config → Verify again             │
│  6. Results correct? → Generate C++ code                          │
│                                                                 │
│  PHASE 2: Mobile (Optional)                                    │
│  7. Click "Generate Android" hoặc "Generate iOS"               │
│  8. Select use case (verify single image / folder / camera)           │
│  9. Generate mobile wrapper code                               │
│                                                                 │
│  Time: 3-5 minutes                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  USER FLOW C: Mobile Only (need C++ first)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  "I only need code for Android/iOS"                           │
│                                                                 │
│  → Still must go through Phase 1 to generate C++ core                      │
│  → C++ core is foundation, mobile code is just wrapper           │
│  → Verify C++ on PC first to ensure logic is correct             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.2.2. Input Dependencies

```
┌─────────────────────────────────────────────────────────────────┐
│  INPUT FILES VÀ DEPENDENCIES                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─ REQUIRED ─────────────────────────────────────────────────┐│
│  │                                                             ││
│  │  📄 ONNX Model File (.onnx)                                ││
│  │     • Required - must have                                     ││
│  │     • Used to: detect architecture, extract I/O shapes     ││
│  │                                                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─ OPTIONAL ─────────────────────────────────────────────────┐│
│  │                                                             ││
│  │  📄 Python Inference Code (.py)                            ││
│  │     • Not required                                       ││
│  │     • Nếu có: Extract exact preprocessing logic            ││
│  │     • If not: Use heuristics + user config             ││
│  │                                                             ││
│  │  📄 Class Labels File (.txt)                               ││
│  │     • Not required                                       ││
│  │     • Nếu có: Generate code với class names                    ││
│  │     • If not: Use class indices (0, 1, 2, ...)        ││
│  │                                                             ││
│  │  🖼️ Test Image (.jpg, .png)                                ││
│  │     • Not required                                       ││
│  │     • Only needed for Verify step                              ││
│  │                                                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  APP BEHAVIOR:                                                  │
│  • No optional inputs → Still can generate code              │
│  • With Python code → Generate more accurate code                   │
│  • Có Labels file → Code có class names                       │
│  • With Test image → Can verify before generating           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3. Wizard Steps Design - Phase 1: C++ Core

#### Step 1: Input

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ONNX Code Generator                                              [─][□][×] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ PHASE 1: C++ Core ────────────────────────────────────────────────┐    │
│  │  ● Input  ──────  ○ Configure  ──────  ○ Verify  ──────  ○ Generate │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║  STEP 1: Input Files                                                  ║ │
│  ╠═══════════════════════════════════════════════════════════════════════╣ │
│  ║                                                                       ║ │
│  ║  ┌─ Required ─────────────────────────────────────────────────────┐  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  ONNX Model    [                              ] [Browse...]    │  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  ┌──────────────────────────────────────────────────────────┐ │  ║ │
│  ║  │  │  ✓ Model loaded: yolov8n.onnx                           │ │  ║ │
│  ║  │  │  • Architecture: YOLOv8 (confidence: 95%)               │ │  ║ │
│  ║  │  │  • Input: 1×3×640×640 (float32)                         │ │  ║ │
│  ║  │  │  • Output: 1×84×8400                                    │ │  ║ │
│  ║  │  │  • Size: 6.3 MB                                         │ │  ║ │
│  ║  │  └──────────────────────────────────────────────────────────┘ │  ║ │
│  ║  │                                                                │  ║ │
│  ║  └────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ║  ┌─ Optional (click to expand) ───────────────────────────── [+] ─┐  ║ │
│  ║  └────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                           [Skip to Generate]  [Next >]│ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Optional section khi expanded:**

```
│  ║  ┌─ Optional ─────────────────────────────────────────────── [-] ─┐  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  Python Inference Code    [                    ] [Browse...]   │  ║ │
│  ║  │  └─ Helps extract exact preprocessing logic                    │  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  Class Labels File        [                    ] [Browse...]   │  ║ │
│  ║  │  └─ .txt file with one class name per line                     │  ║ │
│  ║  │                                                                │  ║ │
└────────────────────────────────────────────────────────────────┘  ║ │
```

#### Step 2: Configure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ONNX Code Generator                                              [─][□][×] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ PHASE 1: C++ Core ────────────────────────────────────────────────┐    │
│  │  ✓ Input  ──────  ● Configure  ──────  ○ Verify  ──────  ○ Generate │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║  STEP 2: Configure C++ Code                                           ║ │
│  ║                                                                       ║ │
│  ║  ┌─ C++ Image Library ─────────────────────────────────────────────┐  ║ │
│  ║  │                                                                 │  ║ │
│  ║  │   ● OpenCV (recommended)                                        │  ║ │
│  ║  │     └─ Best for: PC apps, desktop tools, quick prototyping     │  ║ │
│  ║  │        Features: imread, resize, cvtColor built-in             │  ║ │
│  ║  │        Dependency: Requires OpenCV libs installed              │  ║ │
│  ║  │                                                                 │  ║ │
│  ║  │   ○ stb_image (lightweight, header-only)                        │  ║ │
│  ║  │     └─ Best for: Embedded systems, minimal dependencies        │  ║ │
│  ║  │        Features: Load PNG/JPG, basic decode                    │  ║ │
│  ║  │        Dependency: Single header file (bundled)                │  ║ │
│  ║  │                                                                 │  ║ │
│  ║  │   ○ Raw buffer (no dependencies)                                │  ║ │
│  ║  │     └─ Best for: Camera/video pipelines, Android/iOS native    │  ║ │
│  ║  │        Features: Direct pixel buffer input (RGB/YUV)           │  ║ │
│  ║  │        Dependency: None - caller provides decoded pixels       │  ║ │
│  ║  │                                                                 │  ║ │
│  ║  │   ℹ️ Mobile code (Phase 2) always uses Raw buffer mode.          │  ║ │
│  ║  │      Library selection here only affects PC/Desktop code.        │  ║ │
│  ║  │                                                                 │  ║ │
│  ║  └─────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ║  ┌─ Preprocessing ─────────────────┐ ┌─ Postprocessing ───────────┐  ║ │
│  ║  │  Input Size:  [640]×[640] 🔒   │ │  Type:     [NMS        ▼]  │  ║ │
│  ║  │  Color:       [RGB       ▼]    │ │  Conf:     [0.25       ]   │  ║ │
│  ║  │  Resize:      [Letterbox ▼]    │ │  IoU:      [0.45       ]   │  ║ │
│  ║  │  Normalize:   [✓] /255         │ │  Classes:  [80         ]   │  ║ │
│  ║  │  [Show Advanced ▼]             │ │  [Show Advanced ▼]        │  ║ │
│  ║  └─────────────────────────────────┘ └────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ║                              [Reset to Defaults]                      ║ │
│  ║                                                                       ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  [< Back]                         [Skip to Generate]  [Next: Verify >]│ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Image Library Use Cases Summary:**

```
┌─────────────────────────────────────────────────────────────────┐
│  IMAGE LIBRARY SELECTION GUIDE                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Use Case                        │ Recommended Library          │
│  ────────────────────────────────┼──────────────────────────────│
│  PC desktop app                  │ OpenCV                       │
│  Quick prototyping/testing       │ OpenCV                       │
│  Server-side batch processing    │ OpenCV                       │
│  ────────────────────────────────┼──────────────────────────────│
│  Embedded Linux (Raspberry Pi)   │ stb_image                    │
│  Minimal binary size             │ stb_image                    │
│  No external dependencies        │ stb_image                    │
│  ────────────────────────────────┼──────────────────────────────│
│  Android camera app              │ Raw buffer                   │
│  iOS camera app                  │ Raw buffer                   │
│  Video pipeline integration      │ Raw buffer                   │
│  Custom image source             │ Raw buffer                   │
│                                                                 │
│  NOTE: Phase 2 mobile code LUÔN sinh Raw buffer mode           │
│        because camera APIs already provide decoded pixels.              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Step 3: Verify (Recommended)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ONNX Code Generator                                              [─][□][×] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ PHASE 1: C++ Core ────────────────────────────────────────────────┐    │
│  │  ✓ Input  ──────  ✓ Configure  ──────  ● Verify  ──────  ○ Generate │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║  STEP 3: Verify Code                                                  ║ │
│  ║                                                                       ║ │
│  ║  ┌─ Why Verify? ──────────────────────────────────────────────────┐  ║ │
│  ║  │  Test code on PC TRƯỚC KHI sinh code cho mobile.             │  ║ │
│  ║  │  Ensure preprocessing/postprocessing logic is correct.              │  ║ │
│  ║  └────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ║  ┌─ Verification Options ─────────────────────────────────────────┐  ║ │
│  ║  │                                                                 │  ║ │
│  ║  │  [✓] Verify Python code (user-provided)                         │  ║ │
│  ║  │      └─ Run detect.py with test image to confirm code is correct    │  ║ │
│  ║  │                                                                 │  ║ │
│  ║  │  [✓] Verify C++ code (tool-generated)                           │  ║ │
│  ║  │      └─ Compile + run C++ code, compare with Python             │  ║ │
│  ║  │                                                                 │  ║ │
│  ║  │  ℹ️ If Python code provided: verify Python first to ensure         │  ║ │
│  ║  │     inference logic is correct, then verify C++ to ensure         │  ║ │
│  ║  │     generated code matches Python.                              │  ║ │
│  ║  │                                                                 │  ║ │
│  ║  └─────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ║  ┌─ Test ────────────────────────────────────────────────────────┐   ║ │
│  ║  │                                                               │   ║ │
│  ║  │  ┌─────────────────────────────────────────────────────────┐ │   ║ │
│  ║  │  │                                                         │ │   ║ │
│  ║  │  │              ┌─────────────┐                            │ │   ║ │
│  ║  │  │  ┌────────┐  │   person    │                            │ │   ║ │
│  ║  │  │  │  dog   │  │   0.94      │      ┌───────────┐         │ │   ║ │
│  ║  │  │  │  0.87  │  │             │      │   car     │         │ │   ║ │
│  ║  │  │  └────────┘  │             │      │   0.91    │         │ │   ║ │
│  ║  │  │              └─────────────┘      └───────────┘         │ │   ║ │
│  ║  │  │                                                         │ │   ║ │
│  ║  │  └─────────────────────────────────────────────────────────┘ │   ║ │
│  ║  │                                                               │   ║ │
│  ║  │  [Import Image...]                        [▶ Run Inference]  │   ║ │
│  ║  │                                                               │   ║ │
│  ║  └───────────────────────────────────────────────────────────────┘   ║ │
│  ║                                                                       ║ │
│  ║  ┌─ Results ─────────────────────────────────────────────────────┐   ║ │
│  ║  │                                                                │   ║ │
│  ║  │  ┌─ Python (user code) ────────┐ ┌─ C++ (generated) ────────┐ │   ║ │
│  ║  │  │  ✅ detect.py ran OK        │ │  ✅ Compiled OK          │ │   ║ │
│  ║  │  │  ██ person   0.94           │ │  ██ person   0.94        │ │   ║ │
│  ║  │  │  ██ car      0.91           │ │  ██ car      0.91        │ │   ║ │
│  ║  │  │  ██ dog      0.87           │ │  ██ dog      0.87        │ │   ║ │
│  ║  │  │  Time: 45.2 ms              │ │  Time: 23.4 ms           │ │   ║ │
│  ║  │  └─────────────────────────────┘ └──────────────────────────┘ │   ║ │
│  ║  │                                                                │   ║ │
│  ║  │  ✅ MATCH: Python and C++ results match!                   │   ║ │
│  ║  │                                                                │   ║ │
│  ║  └────────────────────────────────────────────────────────────────┘   ║ │
│  ║                                                                       ║ │
│  ║  ┌─ Verification ─────────────────────────────────────────────────┐  ║ │
│  ║  │  Are boxes and labels correct?                                │  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  [✗ Wrong - Go back Configure]        [✓ Correct - Generate Code] │  ║ │
│  ║  └────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  [< Back]                                         [Skip]  [Generate >]│ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Verification Flow Logic:**

```
┌─────────────────────────────────────────────────────────────────┐
│  VERIFICATION FLOW                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CASE 1: User cung cấp Python code                             │
│  ─────────────────────────────────────                          │
│  Step A: Verify Python code (optional but recommended)      │
│    • Run user Python code with test image                    │
│    • User confirms results are correct                                │
│    • Purpose: Ensure original code is correct BEFORE generating C++       │
│                                                                 │
│  Step B: Verify C++ code (tool-generated)                      │
│    • Compile + run C++ code sinh ra                            │
│    • Compare output with Python                                  │
│    • Purpose: Ensure C++ matches Python                     │
│                                                                 │
│  Flow: Python ✓ → C++ ✓ → Results match ✓ → Generate          │
│                                                                 │
│  CASE 2: User KHÔNG cung cấp Python code                       │
│  ────────────────────────────────────────                       │
│  • Tool auto-generates Python test code (from config)                   │
│  • Only verify C++ vs tool Python                             │
│  • User must manually verify if results are correct               │
│                                                                 │
│  Flow: Tool's Python → C++ ✓ → User confirms → Generate       │
│                                                                 │
│  WHY VERIFY PYTHON CODE?                                        │
│  ───────────────────────                                        │
│  • User Python code may have bugs                            │
│  • Tool extracts config from Python → config may be wrong          │
│  • Verify Python first = ensure baseline is correct                │
│  • If Python wrong → C++ will also be wrong (garbage in, garbage out) │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Step 4: Generate C++ Code

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ONNX Code Generator                                              [─][□][×] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ PHASE 1: C++ Core ────────────────────────────────────────────────┐    │
│  │  ✓ Input  ──────  ✓ Configure  ──────  ✓ Verify  ──────  ● Generate │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║  STEP 4: Generate C++ Code                                            ║ │
│  ║                                                                       ║ │
│  ║  ┌─ Summary ──────────────────────────────────────────────────────┐  ║ │
│  ║  │  Model:      yolov8n.onnx (YOLOv8)                             │  ║ │
│  ║  │  Image Lib:  OpenCV                                            │  ║ │
│  ║  │  Verified:   ✓ Yes (Python + C++ matched)                     │  ║ │
│  ║  └────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ║  ┌─ Generated Files ──────────────────────────────────────────────┐  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  📁 output/cpp/                                                │  ║ │
│  ║  │  ├── 📄 detector.hpp                              [Preview]   │  ║ │
│  ║  │  ├── 📄 detector.cpp                              [Preview]   │  ║ │
│  ║  │  ├── 📄 verify_single.cpp                         [Preview]   │  ║ │
│  ║  │  ├── 📄 CMakeLists.txt                            [Preview]   │  ║ │
│  ║  │  └── 📄 README.md                                 [Preview]   │  ║ │
│  ║  │                                                                │  ║ │
│  ║  └────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ║  ┌─ Phase 1 Complete! ────────────────────────────────────────────┐  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  ✅ C++ code has been verified and generated successfully!               │  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  [📁 Open Output Folder]                                       │  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  ───────────────────────────────────────────────────────────  │  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  Cần code cho mobile?                                         │  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  [🤖 Generate Android Code]   [🍎 Generate iOS Code]          │  ║ │
│  ║  │                                                                │  ║ │
│  ║  └────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  [< Back]                                               [Start New ▶]│ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.4. Wizard Steps Design - Phase 2: Mobile Wrapper

#### Step 5: Mobile Config (khi click Generate Android/iOS)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ONNX Code Generator                                              [─][□][×] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ PHASE 2: Mobile Wrapper ──────────────────────────────────────────┐    │
│  │  ✓ C++ Core  ──────────────  ● Mobile Config  ──────  ○ Generate   │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║  STEP 5: Configure Android Code                                       ║ │
│  ║                                                                       ║ │
│  ║  ┌─ C++ Core (from Phase 1) ──────────────────────────────────────┐  ║ │
│  ║  │  ✅ detector.hpp/cpp verified and ready                        │  ║ │
│  ║  └────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ║  ┌─ Android: Select use case ───────────────────────────────┐  ║ │
│  ║  │                                                                │  ║ │
│  ║  │   ○ Verify single image                                               │  ║ │
│  ║  │     Quick test on device                                     │  ║ │
│  ║  │     Output: image + bboxes, result.txt (YOLO format)             │  ║ │
│  ║  │                                                                │  ║ │
│  ║  │   ○ Verify image folder                                         │  ║ │
│  ║  │     Batch evaluation, calculate mAP                                 │  ║ │
│  ║  │     Output: images + bboxes, results/*.txt (YOLO format)          │  ║ │
│  ║  │                                                                │  ║ │
│  ║  │   ● Camera integration (production)                               │  ║ │
│  ║  │     Real-time detection từ camera                              │  ║ │
│  ║  │     Output: None - only return detections                      │  ║ │
│  ║  │                                                                │  ║ │
│  ║  └────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  [< Back to C++]                                  [Generate Android >]│ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**iOS similar with Swift options.**

#### Step 6: Generate Mobile Code

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ONNX Code Generator                                              [─][□][×] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ PHASE 2: Mobile Wrapper ──────────────────────────────────────────┐    │
│  │  ✓ C++ Core  ──────────────  ✓ Mobile Config  ──────  ● Generate   │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║  STEP 6: Generate Android Code                                        ║ │
│  ║                                                                       ║ │
│  ║  ┌─ Generated Files ──────────────────────────────────────────────┐  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  📁 output/                                                    │  ║ │
│  ║  │  ├── 📁 cpp/                    (from Phase 1)                │  ║ │
│  ║  │  │   ├── detector.hpp                                         │  ║ │
│  ║  │  │   ├── detector.cpp                                         │  ║ │
│  ║  │  │   └── ...                                                  │  ║ │
│  ║  │  │                                                            │  ║ │
│  ║  │  └── 📁 android/                (NEW - Phase 2)               │  ║ │
│  ║  │      ├── 📁 jni/                                              │  ║ │
│  ║  │      │   ├── 📄 detector_jni.cpp            [Preview]        │  ║ │
│  ║  │      │   └── 📄 CMakeLists.txt              [Preview]        │  ║ │
│  ║  │      ├── 📁 kotlin/                                           │  ║ │
│  ║  │      │   ├── 📄 Detector.kt                 [Preview]        │  ║ │
│  ║  │      │   └── 📄 CameraFrameAnalyzer.kt      [Preview]        │  ║ │
│  ║  │      └── 📄 README.md                       [Preview]        │  ║ │
│  ║  │                                                                │  ║ │
│  ║  └────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ║  ┌─ Complete! ────────────────────────────────────────────────────┐  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  ✅ C++ Core + Android wrapper generated!                     │  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  [📁 Open Output Folder]   [🍎 Also Generate iOS]             │  ║ │
│  ║  │                                                                │  ║ │
│  ║  └────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  [< Back]                                               [Start New ▶]│ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.5. Verification Strategy

#### 5.5.1. Principle: Tool verifies what it generates

```
┌─────────────────────────────────────────────────────────────────┐
│  VERIFICATION STRATEGY                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PRINCIPLES:                                                    │
│  • Tool must be responsible for verifying code it generates      │
│  • Do not let users discover errors at deploy time                      │
│  • Verify both Python logic AND C++ code when possible              │
│                                                                 │
│  VERIFICATION LEVELS:                                           │
│                                                                 │
│  1. Python Logic (ALWAYS runs)                                   │
│     • Verify preprocessing, inference, postprocessing          │
│     • Nhanh: < 1 giây                                          │
│     • Baseline to compare with C++                              │
│                                                                 │
│  2. C++ Code (if available environment)                              │
│     • Compile code generated                                     │
│     • Run with same test image                                 │
│     • Compare results với Python                               │
│     • Ensure C++ works correctly                               │
│                                                                 │
│  IF CANNOT VERIFY C++:                                    │
│  • Clear warning in UI                                    │
│  • Still allow generation (user choice)                           │
│  • Generate test files for user to verify later                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.5.2. Platform Verification Capabilities

```
┌─────────────────────────────────────────────────────────────────┐
│  PLATFORM VERIFICATION MATRIX                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Host OS      │ C++ Core │ Android    │ iOS                    │
│  ─────────────┼──────────┼────────────┼────────────────────────│
│  Windows x64  │ ✅ Build │ ✅ Build   │ ❌ Cannot build        │
│               │ ✅ Run   │ ✅ Run*    │ ❌ Cannot run          │
│  ─────────────┼──────────┼────────────┼────────────────────────│
│  Linux x64    │ ✅ Build │ ✅ Build   │ ❌ Cannot build        │
│               │ ✅ Run   │ ✅ Run*    │ ❌ Cannot run          │
│  ─────────────┼──────────┼────────────┼────────────────────────│
│  macOS        │ ✅ Build │ ✅ Build   │ ✅ Build               │
│               │ ✅ Run   │ ✅ Run*    │ ✅ Run**               │
│                                                                 │
│  * Android: requires Android Emulator (x86_64) or device          │
│  ** iOS: requires iOS Simulator or device                         │
│                                                                 │
│  KẾT LUẬN:                                                      │
│  • iOS code can ONLY be verified on macOS                       │
│  • On Windows/Linux: iOS relies on verified C++ core         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.5.3. Two-Phase Verification Logic

```
┌─────────────────────────────────────────────────────────────────┐
│  VERIFICATION FLOW                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE 1: C++ Core Verification (Step 3)                       │
│  ────────────────────────────────────────                       │
│  ✅ Python inference → Baseline, ALWAYS run               │
│  ✅ C++ compile + run → If CMake + compiler + libs available    │
│  ✅ Compare results       → Python vs C++ must match           │
│                                                                 │
│  → C++ Core MUST verify successfully before generating mobile      │
│                                                                 │
│  PHASE 2: Mobile Wrapper (Step 5-6)                            │
│  ──────────────────────────────────                             │
│  Mobile code = C++ core + platform wrapper                     │
│  • C++ core verified in Phase 1 → logic correct                  │
│  • Wrapper is just bridge code → low chance of logic errors        │
│                                                                 │
│  Android:                                                       │
│  • On any OS: can compile with NDK                        │
│  • On any OS: can run with Emulator (if available)             │
│                                                                 │
│  iOS:                                                           │
│  • On macOS: compile + run with Xcode/Simulator              │
│  • On Windows/Linux: ONLY generate code, CANNOT verify      │
│    → Warning: "iOS code generated but cannot be verified       │
│       on this platform. C++ core was verified."               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.5.4. iOS Warning UI (on non-macOS)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║  STEP 5: Configure iOS Code                                           ║ │
│  ║                                                                       ║ │
│  ║  ┌─ ⚠️ Platform Notice ───────────────────────────────────────────┐  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  You are running the tool on Windows/Linux.                       │  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  • iOS code will be generated but CANNOT be verified on this machine │  ║ │
│  ║  │  • C++ core has been verified in Phase 1                          │  ║ │
│  ║  │  • iOS wrapper code is based on verified C++ core              │  ║ │
│  ║  │                                                                │  ║ │
│  ║  │  To verify iOS code, you need:                                     │  ║ │
│  ║  │  • macOS with Xcode installed                                  │  ║ │
│  ║  │  • iOS Simulator or physical device                         │  ║ │
│  ║  │                                                                │  ║ │
│  ║  └────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ║  ┌─ iOS: Select use case ───────────────────────────────────┐  ║ │
│  ║  │   ...                                                          │  ║ │
│  ║  └────────────────────────────────────────────────────────────────┘  ║ │
│  ║                                                                       ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 5.5.5. Verification UI

```
┌─────────────────────────────────────────────────────────────────┐
│  VERIFICATION RESULTS UI                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─ Verification Results ───────────────────────────────────┐  │
│  │                                                           │  │
│  │  Python Logic      ✅ PASSED   45.2ms   3 detections     │  │
│  │  C++ OpenCV        ✅ PASSED   24.3ms   3 detections     │  │
│  │  C++ stb_image     ✅ PASSED   25.1ms   3 detections     │  │
│  │  C++ Android JNI   ⚠️ SKIPPED  (NDK not found)           │  │
│  │                                                           │  │
│  │  ─────────────────────────────────────────────────────── │  │
│  │  Results Match: ✅ YES                                    │  │
│  │  Max Confidence Diff: 0.001                              │  │
│  │  Max Box Diff: 1px                                        │  │
│  │                                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.4.3. Verification Visualization Requirements

```
┌─────────────────────────────────────────────────────────────────┐
│  VERIFICATION VISUALIZATION                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  IMAGE DISPLAY:                                                 │
│  ✅ Show original image with bounding boxes overlay                    │
│  ✅ Each class has its own color (consistent across app)             │
│  ✅ Label format: "class_name confidence" (e.g., "person 0.94")│
│  ✅ Box border: 2-3px, no fill                              │
│  ✅ Label background: same color as box                         │
│  ✅ Label text: white color                                      │
│                                                                 │
│  DETECTION LIST:                                                │
│  ✅ Table với columns: Class, Confidence, Box                  │
│  ✅ Color indicator khớp với box color                         │
│  ✅ Interactive: hover box → highlight row, and vice versa       │
│                                                                 │
│  TIMING INFO:                                                   │
│  ✅ Breakdown: Preprocess | Inference | Postprocess            │
│  ✅ Total time                                                  │
│  ✅ Help user evaluate performance                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.4.4. YOLO Output Format

```
┌─────────────────────────────────────────────────────────────────┐
│  YOLO OUTPUT FORMAT                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  File: image_name.txt (same name as image file)                │
│                                                                 │
│  Format mỗi dòng:                                              │
│  <class_id> <x_center> <y_center> <width> <height> <confidence>│
│                                                                 │
│  Example (beach.txt):                                            │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ 0 0.456 0.523 0.234 0.456 0.94                             ││
│  │ 2 0.234 0.345 0.123 0.234 0.87                             ││
│  │ 0 0.789 0.654 0.198 0.321 0.76                             ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Trong đó:                                                      │
│  • class_id: index of class (0, 1, 2, ...)                   │
│  • x_center, y_center: tâm bbox, normalized [0,1]             │
│  • width, height: bbox size, normalized [0,1]           │
│  • confidence: độ tin cậy [0,1]                               │
│                                                                 │
│  Compatible with:                                              │
│  • YOLO training/evaluation format                             │
│  • pycocotools (sau khi convert)                              │
│  • Popular mAP calculation tools                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.6. UI/UX Checklist

```
┌─────────────────────────────────────────────────────────────────┐
│  CHECKLIST: Does app follow UX principles?           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ Progressive Disclosure                                      │
│     □ Required inputs shown first, clearly                      │
│     □ Optional inputs in collapsible section                │
│     □ Advanced settings ẩn default                            │
│                                                                 │
│  ✅ Two-Phase Wizard                                            │
│     □ Phase 1: Input → Configure → Verify → Generate C++       │
│     □ Phase 2 (optional): Mobile Config → Generate Mobile      │
│     □ Step indicator always visible                                 │
│     □ User knows which step they are on                                │
│                                                                 │
│  ✅ Sensible Defaults                                           │
│     □ Auto-detect from ONNX file                                 │
│     □ User can just: select file → Generate                    │
│     □ No additional config required                            │
│                                                                 │
│  ✅ Immediate Feedback                                          │
│     □ Load ONNX → show model info immediately                         │
│     □ Run verify → show results + timing immediately                  │
│     □ Progress bar for long operations                         │
│                                                                 │
│  ✅ Reversible Actions                                          │
│     □ Back button every step                                     │
│     □ Reset to defaults button                                 │
│     □ "Wrong" → go back to Configure (keep values)                 │
│                                                                 │
│  ✅ Escape Hatches                                              │
│     □ "Skip to Generate" for power users                       │
│     □ "Skip" verify if not needed                              │
│                                                                 │
│  ✅ Error Prevention                                            │
│     □ Disable Next if insufficient input                          │
│     □ Validate input on entry                             │
│     □ Warning if config seems wrong                             │
│     □ Confirm before overwriting files                        │
│                                                                 │
│  ✅ Platform Awareness                                          │
│     □ Warning when generating iOS on non-macOS                     │
│     □ Show verification capability by platform clearly           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. PySide6 GUI Implementation

### 6.1. Qt Platform Handling (Linux XCB Issue)

On Linux, Qt GUI apps may encounter XCB errors when missing dependencies or running headless:

```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
This application failed to start because no Qt platform plugin could be initialized
```

#### 6.1.1. Qt Platform Plugins

```
┌─────────────────────────────────────────────────────────────────┐
│  QT PLATFORM PLUGINS                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Qt supports multiple "platform plugins" for UI rendering:              │
│                                                                 │
│  ┌─────────────┬────────────────────────────────────────────┐  │
│  │ Plugin      │ Description                                      │  │
│  ├─────────────┼────────────────────────────────────────────┤  │
│  │ xcb         │ Linux X11 - display UI on screen         │  │
│  │ wayland     │ Linux Wayland - display UI on screen     │  │
│  │ windows     │ Windows - display UI on screen           │  │
│  │ cocoa       │ macOS - display UI on screen             │  │
│  │ offscreen   │ Render to memory, NO screen required     │  │
│  └─────────────┴────────────────────────────────────────────┘  │
│                                                                 │
│  OFFSCREEN MODE:                                                │
│  • App still runs normally (logic, events, widgets, etc.)    │
│  • UI is rendered to buffer in RAM                         │
│  • No window displayed on screen                             │
│  • Used for: headless servers, Docker, CI/CD, testing         │
│                                                                 │
│  VÍ DỤ:                                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Server (no monitor)                               │  │
│  │  ┌─────────┐     ┌─────────┐                            │  │
│  │  │ Qt App  │ ──▶ │ Memory  │  (offscreen - no display)  │  │
│  │  └─────────┘     └─────────┘                            │  │
│  │                                                          │  │
│  │  Desktop (with monitor)                                    │  │
│  │  ┌─────────┐     ┌─────────┐     ┌─────────┐           │  │
│  │  │ Qt App  │ ──▶ │   XCB   │ ──▶ │ Monitor │           │  │
│  │  └─────────┘     └─────────┘     └─────────┘           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.1.2. Required Linux Dependencies

```bash
# Ubuntu/Debian - install XCB dependencies
sudo apt install \
    libxcb1 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-glx0 \
    libxcb-util1 \
    libxkbcommon-x11-0 \
    libxcb-xkb1

# Debug to see which library is missing
QT_DEBUG_PLUGINS=1 python -c "from PySide6.QtWidgets import QApplication"
```

#### 6.1.3. Application Entry Point với Platform Handling

```python
# main.py - Entry point with Qt platform handling

import sys
import os
from pathlib import Path


def setup_qt_platform():
    """
    Handle Qt platform issues on Linux.
    MUST be called BEFORE any Qt imports.
    """
    if sys.platform != "linux":
        return  # Windows/macOS does not need handling
    
    # Check if running headless (no display)
    has_display = bool(
        os.environ.get("DISPLAY") or 
        os.environ.get("WAYLAND_DISPLAY")
    )
    
    if not has_display:
        print("Warning: No display detected, using offscreen mode")
        print("         GUI will not be visible on screen")
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    
    # Optional: Enable debug logging for Qt plugins
    # os.environ["QT_DEBUG_PLUGINS"] = "1"


def check_xcb_dependencies():
    """
    Check if XCB dependencies are available.
    Returns list of missing libraries.
    """
    if sys.platform != "linux":
        return []
    
    import ctypes
    
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


def main():
    # Step 1: Setup Qt platform BEFORE any imports
    setup_qt_platform()
    
    # Step 2: Check XCB dependencies on Linux
    missing_libs = check_xcb_dependencies()
    if missing_libs:
        print("Warning: Missing XCB libraries:")
        for lib in missing_libs:
            print(f"  - {lib}")
        print("\nInstall with: sudo apt install libxcb-xinerama0 libxcb-cursor0 ...")
        print("Falling back to offscreen mode\n")
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    
    # Step 3: Now safe to import Qt
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from gui.main_window import MainWindow
    
    # Step 4: Create application
    app = QApplication(sys.argv)
    app.setApplicationName("ONNX CodeGen")
    app.setOrganizationName("ONNXCodeGen")
    
    # Step 5: Create and show main window
    window = MainWindow()
    window.show()
    
    # Step 6: Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

#### 6.1.4. Running in Different Environments

```bash
# Normal desktop (with display)
python -m onnx_codegen

# Headless server / Docker (auto fallback to offscreen)
python -m onnx_codegen

# Force offscreen mode
QT_QPA_PLATFORM=offscreen python -m onnx_codegen

# Debug Qt plugin loading issues
QT_DEBUG_PLUGINS=1 python -m onnx_codegen

# Using virtual framebuffer (alternative to offscreen)
xvfb-run python -m onnx_codegen
```

#### 6.1.5. Docker Considerations

```dockerfile
# Dockerfile cho ONNX CodeGen tool

FROM python:3.11-slim

# Install XCB dependencies cho Qt
RUN apt-get update && apt-get install -y \
    libxcb1 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

# Set offscreen mode by default in Docker
ENV QT_QPA_PLATFORM=offscreen

WORKDIR /app
COPY . .
RUN pip install -e .

CMD ["python", "-m", "onnx_codegen"]
```

---

### 6.2. Main Window

```python
# gui/main_window.py

import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QMenuBar, QMenu, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QSettings, Slot
from PySide6.QtGui import QAction, QIcon, QKeySequence

from .widgets.file_picker import FilePicker
from .widgets.analysis_view import AnalysisView
from .widgets.config_editor import ConfigEditor
from .widgets.code_preview import CodePreview
from .widgets.progress_dialog import ProgressDialog
from .workers.analyze_worker import AnalyzeWorker
from .workers.generate_worker import GenerateWorker

from ..core.analyzer import ONNXAnalyzer
from ..core.detector import ArchitectureDetector
from ..core.config import ModelConfig, ConfigBuilder
from ..core.generator import CodeGenerator


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("ONNX Inference Code Generator")
        self.setMinimumSize(1200, 800)
        
        # State
        self.current_model_path: Optional[str] = None
        self.current_python_path: Optional[str] = None
        self.current_config: Optional[ModelConfig] = None
        self.analyzer: Optional[ONNXAnalyzer] = None
        
        # Setup UI
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_central_widget()
        self._setup_status_bar()
        
        # Load settings
        self._load_settings()
    
    def _setup_menu_bar(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_onnx_action = QAction("Open &ONNX Model...", self)
        open_onnx_action.setShortcut(QKeySequence.Open)
        open_onnx_action.triggered.connect(self._on_open_onnx)
        file_menu.addAction(open_onnx_action)
        
        open_python_action = QAction("Open &Python Code...", self)
        open_python_action.setShortcut("Ctrl+Shift+O")
        open_python_action.triggered.connect(self._on_open_python)
        file_menu.addAction(open_python_action)
        
        file_menu.addSeparator()
        
        save_config_action = QAction("&Save Config...", self)
        save_config_action.setShortcut(QKeySequence.Save)
        save_config_action.triggered.connect(self._on_save_config)
        file_menu.addAction(save_config_action)
        
        load_config_action = QAction("&Load Config...", self)
        load_config_action.triggered.connect(self._on_load_config)
        file_menu.addAction(load_config_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Generate menu
        generate_menu = menubar.addMenu("&Generate")
        
        generate_action = QAction("&Generate Code", self)
        generate_action.setShortcut("Ctrl+G")
        generate_action.triggered.connect(self._on_generate)
        generate_menu.addAction(generate_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self):
        """Setup toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Open ONNX button
        open_onnx_btn = QAction("Open ONNX", self)
        open_onnx_btn.triggered.connect(self._on_open_onnx)
        toolbar.addAction(open_onnx_btn)
        
        # Open Python button
        open_python_btn = QAction("Open Python", self)
        open_python_btn.triggered.connect(self._on_open_python)
        toolbar.addAction(open_python_btn)
        
        toolbar.addSeparator()
        
        # Generate button
        self.generate_btn = QAction("Generate Code", self)
        self.generate_btn.triggered.connect(self._on_generate)
        self.generate_btn.setEnabled(False)
        toolbar.addAction(self.generate_btn)
    
    def _setup_central_widget(self):
        """Setup central widget with splitters."""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QHBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: File picker + Analysis
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # File picker
        self.file_picker = FilePicker()
        self.file_picker.onnx_file_changed.connect(self._on_onnx_file_changed)
        self.file_picker.python_file_changed.connect(self._on_python_file_changed)
        left_layout.addWidget(self.file_picker)
        
        # Analysis view
        self.analysis_view = AnalysisView()
        left_layout.addWidget(self.analysis_view, stretch=1)
        
        main_splitter.addWidget(left_widget)
        
        # Middle panel: Config editor
        self.config_editor = ConfigEditor()
        self.config_editor.config_changed.connect(self._on_config_changed)
        main_splitter.addWidget(self.config_editor)
        
        # Right panel: Code preview
        self.code_preview = CodePreview()
        main_splitter.addWidget(self.code_preview)
        
        # Set splitter sizes
        main_splitter.setSizes([300, 350, 450])
        
        layout.addWidget(main_splitter)
    
    def _setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _load_settings(self):
        """Load application settings."""
        settings = QSettings("ONNXCodeGen", "MainWindow")
        
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = settings.value("windowState")
        if state:
            self.restoreState(state)
    
    def _save_settings(self):
        """Save application settings."""
        settings = QSettings("ONNXCodeGen", "MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
    
    def closeEvent(self, event):
        """Handle window close."""
        self._save_settings()
        event.accept()
    
    # ─────────────────────────────────────────────────────────────
    # Slots
    # ─────────────────────────────────────────────────────────────
    
    @Slot()
    def _on_open_onnx(self):
        """Open ONNX file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select ONNX Model",
            "",
            "ONNX Files (*.onnx);;All Files (*)"
        )
        if file_path:
            self.file_picker.set_onnx_file(file_path)
    
    @Slot()
    def _on_open_python(self):
        """Open Python file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Python Inference Code",
            "",
            "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.file_picker.set_python_file(file_path)
    
    @Slot(str)
    def _on_onnx_file_changed(self, file_path: str):
        """Handle ONNX file selection."""
        self.current_model_path = file_path
        self._analyze_model()
    
    @Slot(str)
    def _on_python_file_changed(self, file_path: str):
        """Handle Python file selection."""
        self.current_python_path = file_path
        if self.current_config:
            self._update_config_from_python()
    
    def _analyze_model(self):
        """Analyze the selected ONNX model."""
        if not self.current_model_path:
            return
        
        # Show progress dialog
        progress = ProgressDialog("Analyzing Model", self)
        progress.show()
        
        # Create worker thread
        self.analyze_worker = AnalyzeWorker(self.current_model_path)
        self.analyze_worker.progress.connect(progress.set_progress)
        self.analyze_worker.finished.connect(
            lambda info, detection: self._on_analysis_complete(info, detection, progress)
        )
        self.analyze_worker.error.connect(
            lambda msg: self._on_analysis_error(msg, progress)
        )
        self.analyze_worker.start()
    
    def _on_analysis_complete(self, model_info, detection, progress):
        """Handle analysis completion."""
        progress.close()
        
        # Update analysis view
        self.analysis_view.set_model_info(model_info)
        self.analysis_view.set_detection_result(detection)
        
        # Build config
        self.analyzer = ONNXAnalyzer(self.current_model_path)
        builder = ConfigBuilder()
        builder.from_onnx(self.analyzer)
        
        # Add Python info if available
        if self.current_python_path:
            self._update_config_from_python(builder)
        
        self.current_config = builder.build()
        
        # Update config editor
        self.config_editor.set_config(self.current_config)
        
        # Enable generate button
        self.generate_btn.setEnabled(True)
        
        self.status_bar.showMessage(
            f"Analyzed: {Path(self.current_model_path).name} - "
            f"Detected: {detection.architecture.name} ({detection.confidence:.0%})"
        )
    
    def _on_analysis_error(self, message, progress):
        """Handle analysis error."""
        progress.close()
        QMessageBox.critical(self, "Analysis Error", message)
        self.status_bar.showMessage("Analysis failed")
    
    def _update_config_from_python(self, builder=None):
        """Update config with Python code info."""
        if not self.current_python_path:
            return
        
        try:
            with open(self.current_python_path, 'r') as f:
                python_code = f.read()
            
            from ..core.parser import PythonInferenceParser
            parser = PythonInferenceParser(python_code)
            
            if builder:
                builder.from_python(parser)
            elif self.current_config:
                # Update existing config
                parsed = parser.parse()
                if parsed.conf_threshold:
                    self.current_config.postprocess.conf_threshold = parsed.conf_threshold
                if parsed.iou_threshold:
                    self.current_config.postprocess.iou_threshold = parsed.iou_threshold
                self.config_editor.set_config(self.current_config)
        
        except Exception as e:
            QMessageBox.warning(
                self, "Parse Warning",
                f"Could not parse Python file:\n{e}"
            )
    
    @Slot()
    def _on_config_changed(self):
        """Handle config changes from editor."""
        self.current_config = self.config_editor.get_config()
    
    @Slot()
    def _on_generate(self):
        """Generate code."""
        if not self.current_config:
            QMessageBox.warning(self, "No Config", "Please load an ONNX model first.")
            return
        
        # Ask for output directory
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not output_dir:
            return
        
        # Update config from editor
        self.current_config = self.config_editor.get_config()
        
        # Show progress
        progress = ProgressDialog("Generating Code", self)
        progress.show()
        
        # Create worker
        self.generate_worker = GenerateWorker(
            self.current_config,
            output_dir,
            self.current_python_path
        )
        self.generate_worker.progress.connect(progress.set_progress)
        self.generate_worker.finished.connect(
            lambda files: self._on_generate_complete(files, progress)
        )
        self.generate_worker.error.connect(
            lambda msg: self._on_generate_error(msg, progress)
        )
        self.generate_worker.start()
    
    def _on_generate_complete(self, generated_files, progress):
        """Handle generation completion."""
        progress.close()
        
        # Show preview
        if 'source' in generated_files:
            with open(generated_files['source'], 'r') as f:
                self.code_preview.set_code(f.read(), language='cpp')
        
        # Show success message
        file_list = "\n".join(f"• {name}: {path}" for name, path in generated_files.items())
        QMessageBox.information(
            self,
            "Generation Complete",
            f"Successfully generated files:\n\n{file_list}"
        )
        
        self.status_bar.showMessage(f"Generated {len(generated_files)} files")
    
    def _on_generate_error(self, message, progress):
        """Handle generation error."""
        progress.close()
        QMessageBox.critical(self, "Generation Error", message)
    
    @Slot()
    def _on_save_config(self):
        """Save current config to file."""
        if not self.current_config:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            "model_config.yaml",
            "YAML Files (*.yaml);;JSON Files (*.json)"
        )
        
        if file_path:
            self.current_config = self.config_editor.get_config()
            if file_path.endswith('.json'):
                self.current_config.to_json(file_path)
            else:
                self.current_config.to_yaml(file_path)
            self.status_bar.showMessage(f"Config saved to {file_path}")
    
    @Slot()
    def _on_load_config(self):
        """Load config from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Configuration",
            "",
            "YAML Files (*.yaml);;JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.current_config = ModelConfig.from_yaml(file_path)
                self.config_editor.set_config(self.current_config)
                self.generate_btn.setEnabled(True)
                self.status_bar.showMessage(f"Config loaded from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Load Error", str(e))
    
    @Slot()
    def _on_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About ONNX Code Generator",
            "ONNX Inference Code Generator v4\n\n"
            "Generate C++/Python inference code from ONNX models.\n\n"
            "Supports:\n"
            "• YOLOv5/v8/v11\n"
            "• DETR\n"
            "• SSD/MobileNet\n"
            "• End-to-End models"
        )


def run_gui():
    """Entry point for GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("ONNX Code Generator")
    app.setOrganizationName("ONNXCodeGen")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
```

### 6.3. File Picker Widget

```python
# gui/widgets/file_picker.py

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QLineEdit, QFileDialog
)
from PySide6.QtCore import Signal


class FilePicker(QWidget):
    """Widget for selecting ONNX and Python files."""
    
    onnx_file_changed = Signal(str)
    python_file_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Group box
        group = QGroupBox("Input Files")
        group_layout = QVBoxLayout(group)
        
        # ONNX file row
        onnx_layout = QHBoxLayout()
        onnx_layout.addWidget(QLabel("ONNX Model:"))
        
        self.onnx_path_edit = QLineEdit()
        self.onnx_path_edit.setReadOnly(True)
        self.onnx_path_edit.setPlaceholderText("Select ONNX file...")
        onnx_layout.addWidget(self.onnx_path_edit, stretch=1)
        
        self.onnx_browse_btn = QPushButton("Browse...")
        self.onnx_browse_btn.clicked.connect(self._browse_onnx)
        onnx_layout.addWidget(self.onnx_browse_btn)
        
        group_layout.addLayout(onnx_layout)
        
        # ONNX file info
        self.onnx_info_label = QLabel("")
        self.onnx_info_label.setStyleSheet("color: gray; font-size: 11px;")
        group_layout.addWidget(self.onnx_info_label)
        
        # Python file row
        python_layout = QHBoxLayout()
        python_layout.addWidget(QLabel("Python Code:"))
        
        self.python_path_edit = QLineEdit()
        self.python_path_edit.setReadOnly(True)
        self.python_path_edit.setPlaceholderText("(Optional) Select Python inference file...")
        python_layout.addWidget(self.python_path_edit, stretch=1)
        
        self.python_browse_btn = QPushButton("Browse...")
        self.python_browse_btn.clicked.connect(self._browse_python)
        python_layout.addWidget(self.python_browse_btn)
        
        self.python_clear_btn = QPushButton("Clear")
        self.python_clear_btn.clicked.connect(self._clear_python)
        self.python_clear_btn.setEnabled(False)
        python_layout.addWidget(self.python_clear_btn)
        
        group_layout.addLayout(python_layout)
        
        # Python info label
        self.python_info_label = QLabel("Mode: ONNX-only (heuristic detection)")
        self.python_info_label.setStyleSheet("color: #ff9800; font-size: 11px;")
        group_layout.addWidget(self.python_info_label)
        
        layout.addWidget(group)
    
    def _browse_onnx(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select ONNX Model",
            "",
            "ONNX Files (*.onnx);;All Files (*)"
        )
        if file_path:
            self.set_onnx_file(file_path)
    
    def _browse_python(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Python Inference Code",
            "",
            "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.set_python_file(file_path)
    
    def _clear_python(self):
        self.python_path_edit.clear()
        self.python_clear_btn.setEnabled(False)
        self.python_info_label.setText("Mode: ONNX-only (heuristic detection)")
        self.python_info_label.setStyleSheet("color: #ff9800; font-size: 11px;")
        self.python_file_changed.emit("")
    
    def set_onnx_file(self, file_path: str):
        """Set ONNX file path."""
        self.onnx_path_edit.setText(file_path)
        
        # Show file info
        path = Path(file_path)
        size_mb = path.stat().st_size / (1024 * 1024)
        self.onnx_info_label.setText(f"Size: {size_mb:.1f} MB")
        
        self.onnx_file_changed.emit(file_path)
    
    def set_python_file(self, file_path: str):
        """Set Python file path."""
        self.python_path_edit.setText(file_path)
        self.python_clear_btn.setEnabled(True)
        self.python_info_label.setText("Mode: ONNX + Python (high confidence)")
        self.python_info_label.setStyleSheet("color: #4caf50; font-size: 11px;")
        self.python_file_changed.emit(file_path)
    
    def get_onnx_file(self) -> str:
        return self.onnx_path_edit.text()
    
    def get_python_file(self) -> str:
        return self.python_path_edit.text()
```

### 6.4. Analysis View Widget

```python
# gui/widgets/analysis_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout,
    QLabel, QTreeWidget, QTreeWidgetItem, QTextEdit
)
from PySide6.QtCore import Qt

from ...core.analyzer import ONNXModelInfo
from ...core.detector import DetectionResult


class AnalysisView(QWidget):
    """Widget displaying ONNX model analysis results."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Model info group
        info_group = QGroupBox("Model Information")
        info_layout = QFormLayout(info_group)
        
        self.arch_label = QLabel("-")
        self.arch_label.setStyleSheet("font-weight: bold;")
        info_layout.addRow("Architecture:", self.arch_label)
        
        self.confidence_label = QLabel("-")
        info_layout.addRow("Confidence:", self.confidence_label)
        
        self.file_size_label = QLabel("-")
        info_layout.addRow("File Size:", self.file_size_label)
        
        self.opset_label = QLabel("-")
        info_layout.addRow("Opset:", self.opset_label)
        
        self.producer_label = QLabel("-")
        info_layout.addRow("Producer:", self.producer_label)
        
        layout.addWidget(info_group)
        
        # I/O info group
        io_group = QGroupBox("Input / Output")
        io_layout = QVBoxLayout(io_group)
        
        self.io_tree = QTreeWidget()
        self.io_tree.setHeaderLabels(["Name", "Shape", "Type"])
        self.io_tree.setRootIsDecorated(True)
        io_layout.addWidget(self.io_tree)
        
        layout.addWidget(io_group)
        
        # Evidence group
        evidence_group = QGroupBox("Detection Evidence")
        evidence_layout = QVBoxLayout(evidence_group)
        
        self.evidence_text = QTextEdit()
        self.evidence_text.setReadOnly(True)
        self.evidence_text.setMaximumHeight(100)
        evidence_layout.addWidget(self.evidence_text)
        
        layout.addWidget(evidence_group)
    
    def set_model_info(self, info: ONNXModelInfo):
        """Update display with model info."""
        self.file_size_label.setText(f"{info.file_size_mb:.1f} MB")
        self.opset_label.setText(str(info.opset_version))
        self.producer_label.setText(info.producer_name or "Unknown")
        
        # Update I/O tree
        self.io_tree.clear()
        
        # Inputs
        inputs_item = QTreeWidgetItem(["Inputs", "", ""])
        inputs_item.setExpanded(True)
        for inp in info.inputs:
            shape_str = str(inp.shape)
            if inp.is_dynamic:
                shape_str += " (dynamic)"
            item = QTreeWidgetItem([inp.name, shape_str, inp.dtype])
            inputs_item.addChild(item)
        self.io_tree.addTopLevelItem(inputs_item)
        
        # Outputs
        outputs_item = QTreeWidgetItem(["Outputs", "", ""])
        outputs_item.setExpanded(True)
        for out in info.outputs:
            shape_str = str(out.shape)
            if out.is_dynamic:
                shape_str += " (dynamic)"
            item = QTreeWidgetItem([out.name, shape_str, out.dtype])
            outputs_item.addChild(item)
        self.io_tree.addTopLevelItem(outputs_item)
        
        # Resize columns
        for i in range(3):
            self.io_tree.resizeColumnToContents(i)
    
    def set_detection_result(self, result: DetectionResult):
        """Update display with detection result."""
        self.arch_label.setText(result.architecture.name)
        
        # Color code confidence
        conf_percent = result.confidence * 100
        if conf_percent >= 80:
            color = "#4caf50"  # Green
        elif conf_percent >= 50:
            color = "#ff9800"  # Orange
        else:
            color = "#f44336"  # Red
        
        self.confidence_label.setText(f"{conf_percent:.0f}%")
        self.confidence_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # Evidence
        evidence_text = "\n".join(f"• {e}" for e in result.evidence)
        self.evidence_text.setText(evidence_text or "No evidence available")
```

### 6.5. Config Editor Widget

```python
# gui/widgets/config_editor.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QFormLayout, QLabel, QLineEdit, QSpinBox,
    QDoubleSpinBox, QComboBox, QCheckBox, QScrollArea
)
from PySide6.QtCore import Signal

from ...core.config import (
    ModelConfig, PreprocessConfig, PostprocessConfig,
    ColorFormat, ResizeMode, PostprocessType
)


class ConfigEditor(QWidget):
    """Widget for editing model configuration."""
    
    config_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for config
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # ─────────────────────────────────────────────────────────────
        # Preprocessing group
        # ─────────────────────────────────────────────────────────────
        preprocess_group = QGroupBox("Preprocessing")
        preprocess_layout = QFormLayout(preprocess_group)
        
        # Input size
        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(32, 4096)
        self.width_spin.setValue(640)
        self.width_spin.valueChanged.connect(self._on_value_changed)
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("×"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(32, 4096)
        self.height_spin.setValue(640)
        self.height_spin.valueChanged.connect(self._on_value_changed)
        size_layout.addWidget(self.height_spin)
        preprocess_layout.addRow("Input Size:", size_layout)
        
        # Color format
        self.color_combo = QComboBox()
        self.color_combo.addItems(["RGB", "BGR"])
        self.color_combo.currentTextChanged.connect(self._on_value_changed)
        preprocess_layout.addRow("Color Format:", self.color_combo)
        
        # Resize mode
        self.resize_combo = QComboBox()
        self.resize_combo.addItems(["letterbox", "resize", "crop"])
        self.resize_combo.currentTextChanged.connect(self._on_value_changed)
        preprocess_layout.addRow("Resize Mode:", self.resize_combo)
        
        # Image input mode
        self.image_input_combo = QComboBox()
        self.image_input_combo.addItems([
            "opencv",      # OpenCV (default, full features)
            "raw_buffer",  # Raw Buffer (no dependencies)
            "android",     # Android Native (JNI + Bitmap)
            "ios",         # iOS Native (CVPixelBuffer)
            "stb_image"    # stb_image (lightweight)
        ])
        self.image_input_combo.currentTextChanged.connect(self._on_value_changed)
        preprocess_layout.addRow("Image Input:", self.image_input_combo)
        
        # Normalize
        self.normalize_check = QCheckBox("Normalize (÷255)")
        self.normalize_check.setChecked(True)
        self.normalize_check.stateChanged.connect(self._on_value_changed)
        preprocess_layout.addRow("", self.normalize_check)
        
        # Mean values
        mean_layout = QHBoxLayout()
        self.mean_edits = []
        for i in range(3):
            edit = QDoubleSpinBox()
            edit.setRange(-255, 255)
            edit.setDecimals(3)
            edit.setValue(0.0)
            edit.valueChanged.connect(self._on_value_changed)
            self.mean_edits.append(edit)
            mean_layout.addWidget(edit)
        preprocess_layout.addRow("Mean (R,G,B):", mean_layout)
        
        # Std values
        std_layout = QHBoxLayout()
        self.std_edits = []
        for i in range(3):
            edit = QDoubleSpinBox()
            edit.setRange(0.001, 255)
            edit.setDecimals(3)
            edit.setValue(1.0)
            edit.valueChanged.connect(self._on_value_changed)
            self.std_edits.append(edit)
            std_layout.addWidget(edit)
        preprocess_layout.addRow("Std (R,G,B):", std_layout)
        
        scroll_layout.addWidget(preprocess_group)
        
        # ─────────────────────────────────────────────────────────────
        # Postprocessing group
        # ─────────────────────────────────────────────────────────────
        postprocess_group = QGroupBox("Postprocessing")
        postprocess_layout = QFormLayout(postprocess_group)
        
        # Type
        self.postprocess_type_combo = QComboBox()
        self.postprocess_type_combo.addItems([
            "nms", "soft_nms", "threshold", "anchor_nms", "direct", "softmax"
        ])
        self.postprocess_type_combo.currentTextChanged.connect(self._on_value_changed)
        postprocess_layout.addRow("Type:", self.postprocess_type_combo)
        
        # Confidence threshold
        self.conf_spin = QDoubleSpinBox()
        self.conf_spin.setRange(0.0, 1.0)
        self.conf_spin.setSingleStep(0.05)
        self.conf_spin.setDecimals(2)
        self.conf_spin.setValue(0.25)
        self.conf_spin.valueChanged.connect(self._on_value_changed)
        postprocess_layout.addRow("Conf Threshold:", self.conf_spin)
        
        # IoU threshold
        self.iou_spin = QDoubleSpinBox()
        self.iou_spin.setRange(0.0, 1.0)
        self.iou_spin.setSingleStep(0.05)
        self.iou_spin.setDecimals(2)
        self.iou_spin.setValue(0.45)
        self.iou_spin.valueChanged.connect(self._on_value_changed)
        postprocess_layout.addRow("IoU Threshold:", self.iou_spin)
        
        # Num classes
        self.num_classes_spin = QSpinBox()
        self.num_classes_spin.setRange(1, 10000)
        self.num_classes_spin.setValue(80)
        self.num_classes_spin.valueChanged.connect(self._on_value_changed)
        postprocess_layout.addRow("Num Classes:", self.num_classes_spin)
        
        scroll_layout.addWidget(postprocess_group)
        
        # ─────────────────────────────────────────────────────────────
        # Target group
        # ─────────────────────────────────────────────────────────────
        target_group = QGroupBox("Target")
        target_layout = QFormLayout(target_group)
        
        # Language
        self.language_combo = QComboBox()
        self.language_combo.addItems(["cpp", "python", "both"])
        self.language_combo.currentTextChanged.connect(self._on_value_changed)
        target_layout.addRow("Language:", self.language_combo)
        
        # Platform
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["android", "ios", "linux", "windows"])
        self.platform_combo.currentTextChanged.connect(self._on_value_changed)
        target_layout.addRow("Platform:", self.platform_combo)
        
        scroll_layout.addWidget(target_group)
        
        # Add stretch
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
    
    def _on_value_changed(self):
        """Emit signal when any value changes."""
        self.config_changed.emit()
    
    def set_config(self, config: ModelConfig):
        """Set config and update UI."""
        self._config = config
        
        # Block signals during update
        self.blockSignals(True)
        
        # Preprocessing
        pre = config.preprocess
        self.width_spin.setValue(pre.input_width)
        self.height_spin.setValue(pre.input_height)
        self.color_combo.setCurrentText(pre.color_format.value.upper())
        self.resize_combo.setCurrentText(pre.resize_mode.value)
        self.image_input_combo.setCurrentText(pre.image_input_mode.value)
        self.normalize_check.setChecked(pre.normalize)
        for i, val in enumerate(pre.mean):
            self.mean_edits[i].setValue(val)
        for i, val in enumerate(pre.std):
            self.std_edits[i].setValue(val)
        
        # Postprocessing
        post = config.postprocess
        self.postprocess_type_combo.setCurrentText(post.type.value)
        self.conf_spin.setValue(post.conf_threshold)
        self.iou_spin.setValue(post.iou_threshold)
        self.num_classes_spin.setValue(post.num_classes)
        
        # Target
        self.language_combo.setCurrentText(config.target_language)
        self.platform_combo.setCurrentText(config.target_platform)
        
        self.blockSignals(False)
    
    def get_config(self) -> ModelConfig:
        """Get config from UI values."""
        if self._config is None:
            self._config = ModelConfig()
        
        # Preprocessing
        self._config.preprocess.input_width = self.width_spin.value()
        self._config.preprocess.input_height = self.height_spin.value()
        self._config.preprocess.color_format = ColorFormat(
            self.color_combo.currentText().lower()
        )
        self._config.preprocess.resize_mode = ResizeMode(
            self.resize_combo.currentText()
        )
        self._config.preprocess.image_input_mode = ImageInputMode(
            self.image_input_combo.currentText()
        )
        self._config.preprocess.normalize = self.normalize_check.isChecked()
        self._config.preprocess.mean = [e.value() for e in self.mean_edits]
        self._config.preprocess.std = [e.value() for e in self.std_edits]
        
        # Postprocessing
        self._config.postprocess.type = PostprocessType(
            self.postprocess_type_combo.currentText()
        )
        self._config.postprocess.conf_threshold = self.conf_spin.value()
        self._config.postprocess.iou_threshold = self.iou_spin.value()
        self._config.postprocess.num_classes = self.num_classes_spin.value()
        
        # Target
        self._config.target_language = self.language_combo.currentText()
        self._config.target_platform = self.platform_combo.currentText()
        
        return self._config
```

### 6.6. Code Preview Widget

```python
# gui/widgets/code_preview.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QTabWidget,
    QPlainTextEdit, QPushButton, QHBoxLayout, QFileDialog
)
from PySide6.QtGui import QFont, QFontDatabase


class CodePreview(QWidget):
    """Widget for previewing generated code."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._files = {}
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("Generated Code")
        group_layout = QVBoxLayout(group)
        
        # Tab widget for multiple files
        self.tab_widget = QTabWidget()
        group_layout.addWidget(self.tab_widget)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.clicked.connect(self._copy_current)
        btn_layout.addWidget(self.copy_btn)
        
        self.save_btn = QPushButton("Save As...")
        self.save_btn.clicked.connect(self._save_current)
        btn_layout.addWidget(self.save_btn)
        
        group_layout.addLayout(btn_layout)
        
        layout.addWidget(group)
    
    def _get_mono_font(self) -> QFont:
        """Get a monospace font."""
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(10)
        return font
    
    def set_code(self, code: str, language: str = 'cpp', filename: str = None):
        """Set code content."""
        if filename is None:
            filename = f"code.{language}"
        
        # Create text editor
        editor = QPlainTextEdit()
        editor.setPlainText(code)
        editor.setFont(self._get_mono_font())
        editor.setReadOnly(True)
        editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        
        # Add tab
        self.tab_widget.addTab(editor, filename)
        self._files[filename] = code
    
    def set_files(self, files: dict):
        """Set multiple files."""
        self.clear()
        for filename, content in files.items():
            if filename.endswith('.cpp') or filename.endswith('.hpp'):
                lang = 'cpp'
            elif filename.endswith('.py'):
                lang = 'python'
            else:
                lang = 'text'
            self.set_code(content, lang, filename)
    
    def clear(self):
        """Clear all tabs."""
        self.tab_widget.clear()
        self._files.clear()
    
    def _copy_current(self):
        """Copy current tab content to clipboard."""
        current = self.tab_widget.currentWidget()
        if current and isinstance(current, QPlainTextEdit):
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(current.toPlainText())
    
    def _save_current(self):
        """Save current tab content to file."""
        current_index = self.tab_widget.currentIndex()
        if current_index < 0:
            return
        
        filename = self.tab_widget.tabText(current_index)
        current = self.tab_widget.currentWidget()
        
        if current and isinstance(current, QPlainTextEdit):
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save File", filename, "All Files (*)"
            )
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(current.toPlainText())
```

### 6.7. Verification Widget (Step 3)

```python
# gui/widgets/verification_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import time


@dataclass
class Detection:
    """Single detection result."""
    class_id: int
    class_name: str
    confidence: float
    x: int
    y: int
    width: int
    height: int


@dataclass
class InferenceResult:
    """Complete inference result with timing."""
    detections: List[Detection]
    preprocess_time_ms: float
    inference_time_ms: float
    postprocess_time_ms: float
    
    @property
    def total_time_ms(self) -> float:
        return self.preprocess_time_ms + self.inference_time_ms + self.postprocess_time_ms


class DetectionImageViewer(QWidget):
    """Image viewer với detection boxes overlay."""
    
    detection_hovered = Signal(int)
    detection_clicked = Signal(int)
    
    # Consistent colors cho mỗi class
    CLASS_COLORS = [
        QColor(66, 133, 244),   # Blue
        QColor(52, 168, 83),    # Green
        QColor(251, 188, 4),    # Yellow
        QColor(234, 67, 53),    # Red
        QColor(154, 66, 244),   # Purple
        QColor(244, 66, 185),   # Pink
        QColor(66, 244, 212),   # Cyan
        QColor(244, 146, 66),   # Orange
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._image: Optional[np.ndarray] = None
        self._pixmap: Optional[QPixmap] = None
        self._detections: List[Detection] = []
        self._scale_factor: float = 1.0
        self._offset_x: int = 0
        self._offset_y: int = 0
        self._hovered_index: int = -1
        
        self.setMouseTracking(True)
        self.setMinimumSize(400, 300)
    
    def set_image(self, image: np.ndarray):
        """Set image từ numpy array (BGR format từ OpenCV)."""
        import cv2
        self._image = image
        
        h, w, c = image.shape
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        qimage = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        self._pixmap = QPixmap.fromImage(qimage.copy())
        
        self.update()
    
    def set_detections(self, detections: List[Detection]):
        """Set detections to draw on image."""
        self._detections = detections
        self.update()
    
    def clear(self):
        """Clear image and detections."""
        self._image = None
        self._pixmap = None
        self._detections = []
        self.update()
    
    def _get_class_color(self, class_id: int) -> QColor:
        return self.CLASS_COLORS[class_id % len(self.CLASS_COLORS)]
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(245, 245, 245))
        
        if self._pixmap is None:
            painter.setPen(QColor(150, 150, 150))
            painter.setFont(QFont("Arial", 14))
            painter.drawText(
                self.rect(), Qt.AlignCenter,
                "Drag & Drop Image Here\nor click Import"
            )
            return
        
        # Calculate scale to fit image in widget
        widget_w, widget_h = self.width(), self.height()
        img_w, img_h = self._pixmap.width(), self._pixmap.height()
        
        self._scale_factor = min(widget_w / img_w, widget_h / img_h)
        scaled_w = int(img_w * self._scale_factor)
        scaled_h = int(img_h * self._scale_factor)
        
        self._offset_x = (widget_w - scaled_w) // 2
        self._offset_y = (widget_h - scaled_h) // 2
        
        # Draw scaled image
        scaled = self._pixmap.scaled(scaled_w, scaled_h, 
                                      Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(self._offset_x, self._offset_y, scaled)
        
        # Draw detection boxes
        for i, det in enumerate(self._detections):
            self._draw_detection(painter, det, i == self._hovered_index)
    
    def _draw_detection(self, painter: QPainter, det: Detection, is_hovered: bool):
        color = self._get_class_color(det.class_id)
        line_width = 3 if is_hovered else 2
        
        # Scale coordinates to widget space
        x = int(det.x * self._scale_factor) + self._offset_x
        y = int(det.y * self._scale_factor) + self._offset_y
        w = int(det.width * self._scale_factor)
        h = int(det.height * self._scale_factor)
        
        # Draw box
        pen = QPen(color, line_width)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(x, y, w, h)
        
        # Draw label
        label = f"{det.class_name} {det.confidence:.2f}"
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        
        metrics = painter.fontMetrics()
        text_w = metrics.horizontalAdvance(label) + 8
        text_h = metrics.height() + 4
        
        label_y = y - text_h if y > text_h else y
        
        painter.fillRect(x, label_y, text_w, text_h, color)
        painter.setPen(Qt.white)
        painter.drawText(x + 4, label_y + metrics.ascent() + 2, label)
    
    def mouseMoveEvent(self, event):
        """Highlight detection khi hover."""
        pos = event.pos()
        new_hovered = -1
        
        for i, det in enumerate(self._detections):
            x = int(det.x * self._scale_factor) + self._offset_x
            y = int(det.y * self._scale_factor) + self._offset_y
            w = int(det.width * self._scale_factor)
            h = int(det.height * self._scale_factor)
            
            if x <= pos.x() <= x + w and y <= pos.y() <= y + h:
                new_hovered = i
                break
        
        if new_hovered != self._hovered_index:
            self._hovered_index = new_hovered
            self.detection_hovered.emit(new_hovered)
            self.update()


class VerificationWidget(QWidget):
    """Widget cho Step 3: Verify."""
    
    verification_passed = Signal(object)  # Emit config when user confirms correct
    verification_failed = Signal()         # Emit khi user nói sai
    back_requested = Signal()              # Emit when user wants to go back
    skip_requested = Signal()              # Emit khi user muốn skip
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._session = None  # ONNX Runtime session
        self._config = None   # Current config
        self._test_image: Optional[np.ndarray] = None
        self._last_result: Optional[InferenceResult] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Info box
        info_group = QGroupBox("Why Verify?")
        info_layout = QVBoxLayout(info_group)
        info_layout.addWidget(QLabel(
            "Test the model with your config BEFORE generating code.\n"
            "This ensures the generated code will produce correct results."
        ))
        layout.addWidget(info_group)
        
        # Main content: Image + Results
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left: Image viewer
        self.image_viewer = DetectionImageViewer()
        content_splitter.addWidget(self.image_viewer)
        
        # Right: Results + Timing
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Detection table
        det_group = QGroupBox("Detections")
        det_layout = QVBoxLayout(det_group)
        
        self.detection_table = QTableWidget()
        self.detection_table.setColumnCount(3)
        self.detection_table.setHorizontalHeaderLabels(["Class", "Conf", "Box"])
        self.detection_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.detection_table.setSelectionBehavior(QTableWidget.SelectRows)
        det_layout.addWidget(self.detection_table)
        results_layout.addWidget(det_group)
        
        # Timing
        timing_group = QGroupBox("Timing")
        timing_layout = QVBoxLayout(timing_group)
        self.timing_label = QLabel(
            "Preprocess:  - ms\n"
            "Inference:   - ms\n"
            "Postprocess: - ms\n"
            "─────────────────\n"
            "Total:       - ms"
        )
        self.timing_label.setFont(QFont("Consolas", 10))
        timing_layout.addWidget(self.timing_label)
        results_layout.addWidget(timing_group)
        
        results_layout.addStretch()
        content_splitter.addWidget(results_widget)
        content_splitter.setSizes([600, 300])
        
        layout.addWidget(content_splitter)
        
        # Buttons: Import + Run
        btn_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("Import Image...")
        self.import_btn.clicked.connect(self._on_import_image)
        
        self.run_btn = QPushButton("▶ Run Inference")
        self.run_btn.setEnabled(False)
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:disabled { background-color: #ccc; }
        """)
        self.run_btn.clicked.connect(self._on_run_inference)
        
        btn_layout.addWidget(self.import_btn)
        btn_layout.addWidget(self.run_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Verification buttons
        verify_group = QGroupBox("Verification")
        verify_layout = QHBoxLayout(verify_group)
        
        verify_layout.addWidget(QLabel("Are boxes and labels correct?"))
        verify_layout.addStretch()
        
        self.wrong_btn = QPushButton("✗ Wrong - Go back Configure")
        self.wrong_btn.setEnabled(False)
        self.wrong_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:disabled { background-color: #ccc; }
        """)
        self.wrong_btn.clicked.connect(self._on_wrong)
        
        self.correct_btn = QPushButton("✓ Correct - Generate Code")
        self.correct_btn.setEnabled(False)
        self.correct_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:disabled { background-color: #ccc; }
        """)
        self.correct_btn.clicked.connect(self._on_correct)
        
        verify_layout.addWidget(self.wrong_btn)
        verify_layout.addWidget(self.correct_btn)
        
        layout.addWidget(verify_group)
        
        # Connect hover sync
        self.image_viewer.detection_hovered.connect(self._on_detection_hovered)
    
    def set_session(self, session):
        """Set ONNX Runtime session."""
        self._session = session
        self._update_run_button()
    
    def set_config(self, config):
        """Set current config."""
        self._config = config
    
    def _on_import_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Test Image", "",
            "Images (*.jpg *.jpeg *.png *.bmp);;All Files (*)"
        )
        if path:
            import cv2
            self._test_image = cv2.imread(path)
            if self._test_image is not None:
                self.image_viewer.set_image(self._test_image)
                self._update_run_button()
    
    def _update_run_button(self):
        can_run = self._session is not None and self._test_image is not None
        self.run_btn.setEnabled(can_run)
    
    def _on_run_inference(self):
        if self._session is None or self._test_image is None:
            return
        
        try:
            result = self._run_inference()
            self._last_result = result
            
            # Update UI
            self.image_viewer.set_detections(result.detections)
            self._update_results_table(result.detections)
            self._update_timing(result)
            
            # Enable verification buttons
            self.correct_btn.setEnabled(True)
            self.wrong_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Inference failed:\n{e}")
    
    def _run_inference(self) -> InferenceResult:
        """Run inference với timing."""
        import cv2
        
        # Preprocess
        t0 = time.perf_counter()
        input_tensor = self._preprocess(self._test_image)
        preprocess_time = (time.perf_counter() - t0) * 1000
        
        # Inference
        t0 = time.perf_counter()
        input_name = self._session.get_inputs()[0].name
        outputs = self._session.run(None, {input_name: input_tensor})
        inference_time = (time.perf_counter() - t0) * 1000
        
        # Postprocess
        t0 = time.perf_counter()
        detections = self._postprocess(
            outputs,
            self._test_image.shape[1],
            self._test_image.shape[0]
        )
        postprocess_time = (time.perf_counter() - t0) * 1000
        
        return InferenceResult(
            detections=detections,
            preprocess_time_ms=preprocess_time,
            inference_time_ms=inference_time,
            postprocess_time_ms=postprocess_time
        )
    
    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image theo config."""
        import cv2
        
        # Get config values
        cfg = self._config
        input_w = cfg.preprocess.input_width
        input_h = cfg.preprocess.input_height
        
        h, w = image.shape[:2]
        
        # Letterbox resize
        scale = min(input_w / w, input_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        
        resized = cv2.resize(image, (new_w, new_h))
        
        padded = np.full((input_h, input_w, 3), 114, dtype=np.uint8)
        pad_x = (input_w - new_w) // 2
        pad_y = (input_h - new_h) // 2
        padded[pad_y:pad_y+new_h, pad_x:pad_x+new_w] = resized
        
        # BGR to RGB
        processed = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        
        # Normalize
        processed = processed.astype(np.float32) / 255.0
        
        # HWC to CHW
        processed = processed.transpose(2, 0, 1)
        
        # Add batch dimension
        return np.expand_dims(processed, axis=0)
    
    def _postprocess(self, outputs, orig_w, orig_h) -> List[Detection]:
        """Postprocess model outputs."""
        cfg = self._config
        conf_threshold = cfg.postprocess.confidence_threshold
        iou_threshold = cfg.postprocess.iou_threshold
        
        output = outputs[0]
        if output.ndim == 3:
            output = output[0].T
        
        boxes = output[:, :4]
        scores = output[:, 4:]
        
        class_ids = np.argmax(scores, axis=1)
        confidences = np.max(scores, axis=1)
        
        mask = confidences > conf_threshold
        boxes = boxes[mask]
        class_ids = class_ids[mask]
        confidences = confidences[mask]
        
        if len(boxes) == 0:
            return []
        
        # cx,cy,w,h to x,y,w,h
        boxes[:, 0] -= boxes[:, 2] / 2
        boxes[:, 1] -= boxes[:, 3] / 2
        
        # Scale to original
        input_w = cfg.preprocess.input_width
        input_h = cfg.preprocess.input_height
        scale = min(input_w / orig_w, input_h / orig_h)
        pad_x = (input_w - orig_w * scale) / 2
        pad_y = (input_h - orig_h * scale) / 2
        
        boxes[:, 0] = (boxes[:, 0] - pad_x) / scale
        boxes[:, 1] = (boxes[:, 1] - pad_y) / scale
        boxes[:, 2] /= scale
        boxes[:, 3] /= scale
        
        # Simple NMS
        indices = self._nms(boxes, confidences, iou_threshold)
        
        class_names = self._get_class_names()
        detections = []
        
        for i in indices[:100]:
            cid = int(class_ids[i])
            det = Detection(
                class_id=cid,
                class_name=class_names[cid] if cid < len(class_names) else f"class_{cid}",
                confidence=float(confidences[i]),
                x=int(boxes[i, 0]),
                y=int(boxes[i, 1]),
                width=int(boxes[i, 2]),
                height=int(boxes[i, 3])
            )
            detections.append(det)
        
        return detections
    
    def _nms(self, boxes, scores, iou_threshold):
        indices = np.argsort(scores)[::-1]
        keep = []
        
        while len(indices) > 0:
            i = indices[0]
            keep.append(i)
            
            if len(indices) == 1:
                break
            
            ious = self._compute_iou(boxes[i], boxes[indices[1:]])
            mask = ious < iou_threshold
            indices = indices[1:][mask]
        
        return keep
    
    def _compute_iou(self, box, boxes):
        x1 = np.maximum(box[0], boxes[:, 0])
        y1 = np.maximum(box[1], boxes[:, 1])
        x2 = np.minimum(box[0] + box[2], boxes[:, 0] + boxes[:, 2])
        y2 = np.minimum(box[1] + box[3], boxes[:, 1] + boxes[:, 3])
        
        inter = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
        area1 = box[2] * box[3]
        area2 = boxes[:, 2] * boxes[:, 3]
        union = area1 + area2 - inter
        
        return inter / (union + 1e-6)
    
    def _get_class_names(self):
        # COCO classes
        return [
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train",
            "truck", "boat", "traffic light", "fire hydrant", "stop sign",
            "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep",
            "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
            "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard",
            "sports ball", "kite", "baseball bat", "baseball glove", "skateboard",
            "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork",
            "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
            "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
            "couch", "potted plant", "bed", "dining table", "toilet", "tv",
            "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave",
            "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase",
            "scissors", "teddy bear", "hair drier", "toothbrush"
        ]
    
    def _update_results_table(self, detections: List[Detection]):
        self.detection_table.setRowCount(len(detections))
        
        for i, det in enumerate(detections):
            color = self.image_viewer._get_class_color(det.class_id)
            
            class_item = QTableWidgetItem(f"██ {det.class_name}")
            class_item.setForeground(color)
            
            self.detection_table.setItem(i, 0, class_item)
            self.detection_table.setItem(i, 1, QTableWidgetItem(f"{det.confidence:.2f}"))
            self.detection_table.setItem(i, 2, QTableWidgetItem(
                f"[{det.x},{det.y},{det.width},{det.height}]"
            ))
    
    def _update_timing(self, result: InferenceResult):
        self.timing_label.setText(
            f"Preprocess:  {result.preprocess_time_ms:.1f} ms\n"
            f"Inference:   {result.inference_time_ms:.1f} ms\n"
            f"Postprocess: {result.postprocess_time_ms:.1f} ms\n"
            f"─────────────────\n"
            f"Total:       {result.total_time_ms:.1f} ms"
        )
    
    def _on_detection_hovered(self, index: int):
        if index >= 0:
            self.detection_table.selectRow(index)
        else:
            self.detection_table.clearSelection()
    
    def _on_correct(self):
        self.verification_passed.emit(self._config)
    
    def _on_wrong(self):
        self.verification_failed.emit()
```

### 6.8. Worker Threads

```python
# gui/workers/analyze_worker.py

from PySide6.QtCore import QThread, Signal

from ...core.analyzer import ONNXAnalyzer, ONNXModelInfo
from ...core.detector import ArchitectureDetector, DetectionResult


class AnalyzeWorker(QThread):
    """Worker thread for ONNX analysis."""
    
    progress = Signal(int, str)  # percent, message
    finished = Signal(object, object)  # ONNXModelInfo, DetectionResult
    error = Signal(str)
    
    def __init__(self, model_path: str):
        super().__init__()
        self.model_path = model_path
    
    def run(self):
        try:
            # Analyze
            analyzer = ONNXAnalyzer(self.model_path)
            model_info = analyzer.analyze(
                progress_callback=lambda p, m: self.progress.emit(p, m)
            )
            
            # Detect architecture
            self.progress.emit(90, "Detecting architecture...")
            detector = ArchitectureDetector(model_info)
            detection = detector.detect()
            
            self.progress.emit(100, "Done")
            self.finished.emit(model_info, detection)
            
        except Exception as e:
            self.error.emit(str(e))


# gui/workers/generate_worker.py

from PySide6.QtCore import QThread, Signal
from typing import Optional

from ...core.config import ModelConfig
from ...core.generator import CodeGenerator
from ...core.parser import PythonInferenceParser
from ...core.translator import PythonToCppTranslator


class GenerateWorker(QThread):
    """Worker thread for code generation."""
    
    progress = Signal(int, str)
    finished = Signal(dict)  # generated files
    error = Signal(str)
    
    def __init__(
        self,
        config: ModelConfig,
        output_dir: str,
        python_path: Optional[str] = None
    ):
        super().__init__()
        self.config = config
        self.output_dir = output_dir
        self.python_path = python_path
    
    def run(self):
        try:
            self.progress.emit(20, "Preparing...")
            
            generator = CodeGenerator()
            translated_code = None
            
            # Parse Python if available
            if self.python_path:
                self.progress.emit(40, "Parsing Python code...")
                with open(self.python_path, 'r') as f:
                    python_code = f.read()
                
                parser = PythonInferenceParser(python_code)
                # translator = PythonToCppTranslator(parser.parse())
                # translated_code = translator.translate()
            
            self.progress.emit(60, "Generating code...")
            
            generated_files = generator.generate(
                self.config,
                self.output_dir,
                translated_code
            )
            
            self.progress.emit(100, "Done")
            self.finished.emit(generated_files)
            
        except Exception as e:
            self.error.emit(str(e))
```

### 6.9. Progress Dialog

```python
# gui/widgets/progress_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar
)
from PySide6.QtCore import Qt, Slot


class ProgressDialog(QDialog):
    """Simple progress dialog."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 100)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint
        )
        
        layout = QVBoxLayout(self)
        
        self.message_label = QLabel("Initializing...")
        layout.addWidget(self.message_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
    
    @Slot(int, str)
    def set_progress(self, percent: int, message: str):
        """Update progress."""
        self.progress_bar.setValue(percent)
        self.message_label.setText(message)
```

### 6.10. Code Generator Module

Code Generator module sinh C++ code từ ModelConfig.

```python
# core/generator.py

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from string import Template
from enum import Enum

from .config import (
    ModelConfig, PreprocessConfig, PostprocessConfig,
    ResizeMode, ColorFormat, PostprocessType, ImageInputMode
)


class TargetPlatform(Enum):
    """Target platform cho code generation."""
    PC_OPENCV = "pc_opencv"
    PC_STB = "pc_stb"
    PC_RAW = "pc_raw"
    ANDROID = "android"
    IOS = "ios"


class UseCase(Enum):
    """Use case cho mobile code."""
    VERIFY_SINGLE = "verify_single"
    VERIFY_FOLDER = "verify_folder"
    CAMERA = "camera"


@dataclass
class GeneratedFile:
    """Information about a generated file."""
    path: str
    content: str
    description: str


@dataclass
class GenerationResult:
    """Results sinh code."""
    success: bool
    files: List[GeneratedFile] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    output_dir: str = ""


class CodeGenerator:
    """
    Generator to produce C++ code from ModelConfig.
    
    Supports:
    - PC: OpenCV, stb_image, raw buffer modes
    - Android: JNI + Kotlin
    - iOS: ObjC++ bridge + Swift
    """
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.templates_dir = Path(__file__).parent / "templates"
    
    def generate(self, 
                 platform: TargetPlatform,
                 output_dir: str,
                 use_case: Optional[UseCase] = None,
                 progress_callback=None) -> GenerationResult:
        """
        Generate code cho target platform.
        
        Args:
            platform: Target platform
            output_dir: Folder output
            use_case: Use case (cho mobile)
            progress_callback: Optional callback(percent, message)
        """
        result = GenerationResult(success=True, output_dir=output_dir)
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            if platform == TargetPlatform.PC_OPENCV:
                self._generate_pc_opencv(output_dir, result, progress_callback)
            elif platform == TargetPlatform.PC_STB:
                self._generate_pc_stb(output_dir, result, progress_callback)
            elif platform == TargetPlatform.PC_RAW:
                self._generate_pc_raw(output_dir, result, progress_callback)
            elif platform == TargetPlatform.ANDROID:
                self._generate_android(output_dir, use_case or UseCase.CAMERA, result, progress_callback)
            elif platform == TargetPlatform.IOS:
                self._generate_ios(output_dir, use_case or UseCase.CAMERA, result, progress_callback)
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Generation failed: {str(e)}")
        
        return result
    
    def _generate_pc_opencv(self, output_dir: str, result: GenerationResult, callback):
        """Generate code PC với OpenCV."""
        if callback:
            callback(10, "Generating detector.hpp...")
        
        # detector.hpp
        hpp_content = self._render_detector_hpp(ImageInputMode.OPENCV)
        result.files.append(GeneratedFile(
            path=os.path.join(output_dir, "detector.hpp"),
            content=hpp_content,
            description="Detector header file"
        ))
        
        if callback:
            callback(30, "Generating detector.cpp...")
        
        # detector.cpp
        cpp_content = self._render_detector_cpp(ImageInputMode.OPENCV)
        result.files.append(GeneratedFile(
            path=os.path.join(output_dir, "detector.cpp"),
            content=cpp_content,
            description="Detector implementation"
        ))
        
        if callback:
            callback(50, "Generating verify_single.cpp...")
        
        # verify_single.cpp
        main_content = self._render_verify_single(ImageInputMode.OPENCV)
        result.files.append(GeneratedFile(
            path=os.path.join(output_dir, "verify_single.cpp"),
            content=main_content,
            description="Single image verification"
        ))
        
        if callback:
            callback(70, "Generating CMakeLists.txt...")
        
        # CMakeLists.txt
        cmake_content = self._render_cmake(ImageInputMode.OPENCV)
        result.files.append(GeneratedFile(
            path=os.path.join(output_dir, "CMakeLists.txt"),
            content=cmake_content,
            description="CMake build configuration"
        ))
        
        if callback:
            callback(90, "Generating README.md...")
        
        # README.md
        readme_content = self._render_readme(ImageInputMode.OPENCV)
        result.files.append(GeneratedFile(
            path=os.path.join(output_dir, "README.md"),
            content=readme_content,
            description="Build and usage instructions"
        ))
        
        # Write all files
        for f in result.files:
            with open(f.path, 'w', encoding='utf-8') as fp:
                fp.write(f.content)
        
        if callback:
            callback(100, "Done!")
    
    def _generate_android(self, output_dir: str, use_case: UseCase, 
                          result: GenerationResult, callback):
        """Generate code Android."""
        
        # Create directory structure
        jni_dir = os.path.join(output_dir, "jni")
        kotlin_dir = os.path.join(output_dir, "kotlin")
        os.makedirs(jni_dir, exist_ok=True)
        os.makedirs(kotlin_dir, exist_ok=True)
        
        if callback:
            callback(10, "Generating JNI bridge...")
        
        # detector_jni.cpp
        jni_content = self._render_android_jni()
        result.files.append(GeneratedFile(
            path=os.path.join(jni_dir, "detector_jni.cpp"),
            content=jni_content,
            description="JNI bridge implementation"
        ))
        
        if callback:
            callback(30, "Generating native CMakeLists.txt...")
        
        # CMakeLists.txt for JNI
        cmake_content = self._render_android_cmake()
        result.files.append(GeneratedFile(
            path=os.path.join(jni_dir, "CMakeLists.txt"),
            content=cmake_content,
            description="Android NDK CMake configuration"
        ))
        
        if callback:
            callback(50, "Generating Kotlin wrapper...")
        
        # Detector.kt
        kotlin_content = self._render_kotlin_detector()
        result.files.append(GeneratedFile(
            path=os.path.join(kotlin_dir, "Detector.kt"),
            content=kotlin_content,
            description="Kotlin detector wrapper"
        ))
        
        if callback:
            callback(70, "Generating use case code...")
        
        # Use case specific code
        if use_case == UseCase.VERIFY_SINGLE:
            activity_content = self._render_kotlin_verify_single()
            result.files.append(GeneratedFile(
                path=os.path.join(kotlin_dir, "SingleImageVerifier.kt"),
                content=activity_content,
                description="Single image verification activity"
            ))
        elif use_case == UseCase.VERIFY_FOLDER:
            activity_content = self._render_kotlin_verify_folder()
            result.files.append(GeneratedFile(
                path=os.path.join(kotlin_dir, "BatchVerifier.kt"),
                content=activity_content,
                description="Batch verification activity"
            ))
        elif use_case == UseCase.CAMERA:
            analyzer_content = self._render_kotlin_camera()
            result.files.append(GeneratedFile(
                path=os.path.join(kotlin_dir, "CameraFrameAnalyzer.kt"),
                content=analyzer_content,
                description="Camera frame analyzer"
            ))
        
        if callback:
            callback(90, "Generating README.md...")
        
        # README.md
        readme_content = self._render_android_readme(use_case)
        result.files.append(GeneratedFile(
            path=os.path.join(output_dir, "README.md"),
            content=readme_content,
            description="Android integration guide"
        ))
        
        # Write all files
        for f in result.files:
            with open(f.path, 'w', encoding='utf-8') as fp:
                fp.write(f.content)
        
        if callback:
            callback(100, "Done!")
    
    def _generate_ios(self, output_dir: str, use_case: UseCase,
                      result: GenerationResult, callback):
        """Generate code iOS."""
        
        # Create directory structure
        bridge_dir = os.path.join(output_dir, "bridge")
        swift_dir = os.path.join(output_dir, "swift")
        os.makedirs(bridge_dir, exist_ok=True)
        os.makedirs(swift_dir, exist_ok=True)
        
        if callback:
            callback(10, "Generating ObjC++ bridge...")
        
        # DetectorBridge.h
        bridge_h = self._render_ios_bridge_h()
        result.files.append(GeneratedFile(
            path=os.path.join(bridge_dir, "DetectorBridge.h"),
            content=bridge_h,
            description="ObjC++ bridge header"
        ))
        
        # DetectorBridge.mm
        bridge_mm = self._render_ios_bridge_mm()
        result.files.append(GeneratedFile(
            path=os.path.join(bridge_dir, "DetectorBridge.mm"),
            content=bridge_mm,
            description="ObjC++ bridge implementation"
        ))
        
        if callback:
            callback(40, "Generating Swift wrapper...")
        
        # Detector.swift
        swift_content = self._render_swift_detector()
        result.files.append(GeneratedFile(
            path=os.path.join(swift_dir, "Detector.swift"),
            content=swift_content,
            description="Swift detector wrapper"
        ))
        
        if callback:
            callback(60, "Generating use case code...")
        
        # Use case specific code
        if use_case == UseCase.VERIFY_SINGLE:
            view_content = self._render_swift_verify_single()
            result.files.append(GeneratedFile(
                path=os.path.join(swift_dir, "SingleImageVerifier.swift"),
                content=view_content,
                description="Single image verification view"
            ))
        elif use_case == UseCase.VERIFY_FOLDER:
            view_content = self._render_swift_verify_folder()
            result.files.append(GeneratedFile(
                path=os.path.join(swift_dir, "BatchVerifier.swift"),
                content=view_content,
                description="Batch verification view"
            ))
        elif use_case == UseCase.CAMERA:
            processor_content = self._render_swift_camera()
            result.files.append(GeneratedFile(
                path=os.path.join(swift_dir, "CameraFrameProcessor.swift"),
                content=processor_content,
                description="Camera frame processor"
            ))
        
        if callback:
            callback(90, "Generating README.md...")
        
        # README.md
        readme_content = self._render_ios_readme(use_case)
        result.files.append(GeneratedFile(
            path=os.path.join(output_dir, "README.md"),
            content=readme_content,
            description="iOS integration guide"
        ))
        
        # Write all files
        for f in result.files:
            with open(f.path, 'w', encoding='utf-8') as fp:
                fp.write(f.content)
        
        if callback:
            callback(100, "Done!")
    
    # ==================== Template Rendering Methods ====================
    
    def _render_detector_hpp(self, mode: ImageInputMode) -> str:
        """Render detector.hpp template."""
        cfg = self.config
        pre = cfg.preprocess
        post = cfg.postprocess
        
        return f'''// detector.hpp - Auto-generated by ONNX CodeGen
// Model: {Path(cfg.model_path).name}
// Input: {pre.input_width}x{pre.input_height}, {pre.color_format.value.upper()}

#pragma once

#include <vector>
#include <string>
#include <memory>
#include <onnxruntime_cxx_api.h>
{"#include <opencv2/opencv.hpp>" if mode == ImageInputMode.OPENCV else ""}

struct Detection {{
    float x1, y1, x2, y2;  // Bounding box (xyxy format)
    float confidence;
    int class_id;
    std::string class_name;
}};

class Detector {{
public:
    Detector(const std::string& model_path, 
             const std::vector<std::string>& class_names = {{}});
    ~Detector();
    
    // Main detection method
{"    std::vector<Detection> detect(const cv::Mat& image);" if mode == ImageInputMode.OPENCV else "    std::vector<Detection> detect(const uint8_t* rgb_data, int width, int height);"}
    
    // Getters
    int input_width() const {{ return {pre.input_width}; }}
    int input_height() const {{ return {pre.input_height}; }}
    int num_classes() const {{ return {post.num_classes}; }}
    
private:
    // Preprocessing
{"    cv::Mat preprocess(const cv::Mat& image);" if mode == ImageInputMode.OPENCV else "    std::vector<float> preprocess(const uint8_t* rgb_data, int width, int height);"}
    
    // Postprocessing
    std::vector<Detection> postprocess(const std::vector<float>& output,
                                        int orig_width, int orig_height);
    
    // NMS
    std::vector<Detection> nms(std::vector<Detection>& detections,
                               float iou_threshold);
    
    // Members
    std::unique_ptr<Ort::Session> session_;
    Ort::Env env_{{ORT_LOGGING_LEVEL_WARNING, "detector"}};
    std::vector<std::string> class_names_;
    
    // Config
    static constexpr int INPUT_WIDTH = {pre.input_width};
    static constexpr int INPUT_HEIGHT = {pre.input_height};
    static constexpr float CONF_THRESHOLD = {post.confidence_threshold}f;
    static constexpr float IOU_THRESHOLD = {post.iou_threshold}f;
    static constexpr int NUM_CLASSES = {post.num_classes};
}};
'''
    
    def _render_detector_cpp(self, mode: ImageInputMode) -> str:
        """Render detector.cpp template."""
        cfg = self.config
        pre = cfg.preprocess
        
        # Build preprocessing code based on config
        preprocess_code = self._build_preprocess_code(mode)
        postprocess_code = self._build_postprocess_code()
        
        return f'''// detector.cpp - Auto-generated by ONNX CodeGen

#include "detector.hpp"
#include <algorithm>
#include <numeric>
#include <cmath>

Detector::Detector(const std::string& model_path,
                   const std::vector<std::string>& class_names)
    : class_names_(class_names) {{
    
    Ort::SessionOptions session_options;
    session_options.SetIntraOpNumThreads(4);
    session_options.SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_ENABLE_ALL);
    
    session_ = std::make_unique<Ort::Session>(env_, model_path.c_str(), session_options);
}}

Detector::~Detector() = default;

{preprocess_code}

{postprocess_code}

std::vector<Detection> Detector::nms(std::vector<Detection>& detections,
                                      float iou_threshold) {{
    // Sort by confidence (descending)
    std::sort(detections.begin(), detections.end(),
              [](const Detection& a, const Detection& b) {{
                  return a.confidence > b.confidence;
              }});
    
    std::vector<Detection> result;
    std::vector<bool> suppressed(detections.size(), false);
    
    for (size_t i = 0; i < detections.size(); ++i) {{
        if (suppressed[i]) continue;
        
        result.push_back(detections[i]);
        
        for (size_t j = i + 1; j < detections.size(); ++j) {{
            if (suppressed[j]) continue;
            if (detections[i].class_id != detections[j].class_id) continue;
            
            // Calculate IoU
            float x1 = std::max(detections[i].x1, detections[j].x1);
            float y1 = std::max(detections[i].y1, detections[j].y1);
            float x2 = std::min(detections[i].x2, detections[j].x2);
            float y2 = std::min(detections[i].y2, detections[j].y2);
            
            float intersection = std::max(0.0f, x2 - x1) * std::max(0.0f, y2 - y1);
            float area_i = (detections[i].x2 - detections[i].x1) * 
                          (detections[i].y2 - detections[i].y1);
            float area_j = (detections[j].x2 - detections[j].x1) * 
                          (detections[j].y2 - detections[j].y1);
            float iou = intersection / (area_i + area_j - intersection);
            
            if (iou > iou_threshold) {{
                suppressed[j] = true;
            }}
        }}
    }}
    
    return result;
}}
'''
    
    def _build_preprocess_code(self, mode: ImageInputMode) -> str:
        """Build preprocessing code based on config."""
        pre = self.config.preprocess
        
        if mode == ImageInputMode.OPENCV:
            letterbox_code = ""
            if pre.resize_mode == ResizeMode.LETTERBOX:
                letterbox_code = '''
    // Letterbox resize
    float scale = std::min(float(INPUT_WIDTH) / image.cols,
                           float(INPUT_HEIGHT) / image.rows);
    int new_w = int(image.cols * scale);
    int new_h = int(image.rows * scale);
    
    cv::Mat resized;
    cv::resize(image, resized, cv::Size(new_w, new_h));
    
    cv::Mat padded(INPUT_HEIGHT, INPUT_WIDTH, CV_8UC3, cv::Scalar(114, 114, 114));
    int dx = (INPUT_WIDTH - new_w) / 2;
    int dy = (INPUT_HEIGHT - new_h) / 2;
    resized.copyTo(padded(cv::Rect(dx, dy, new_w, new_h)));
    resized = padded;'''
            else:
                letterbox_code = '''
    // Simple resize
    cv::Mat resized;
    cv::resize(image, resized, cv::Size(INPUT_WIDTH, INPUT_HEIGHT));'''
            
            color_convert = ""
            if pre.color_format == ColorFormat.RGB:
                color_convert = '''
    // BGR to RGB
    cv::cvtColor(resized, resized, cv::COLOR_BGR2RGB);'''
            
            normalize_code = ""
            if pre.normalize:
                normalize_code = f'''
    // Normalize to [0, 1]
    resized.convertTo(resized, CV_32FC3, {pre.scale});'''
            
            return f'''cv::Mat Detector::preprocess(const cv::Mat& image) {{
{letterbox_code}
{color_convert}
{normalize_code}
    
    // HWC to CHW
    cv::Mat blob = cv::dnn::blobFromImage(resized);
    return blob;
}}

std::vector<Detection> Detector::detect(const cv::Mat& image) {{
    cv::Mat blob = preprocess(image);
    
    // Create input tensor
    std::vector<int64_t> input_shape = {{1, 3, INPUT_HEIGHT, INPUT_WIDTH}};
    Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(
        OrtArenaAllocator, OrtMemTypeDefault);
    
    Ort::Value input_tensor = Ort::Value::CreateTensor<float>(
        memory_info, (float*)blob.data, blob.total(),
        input_shape.data(), input_shape.size());
    
    // Run inference
    const char* input_names[] = {{"{self.config.input_name}"}};
    const char* output_names[] = {{"{self.config.output_names[0]}"}};
    
    auto outputs = session_->Run(Ort::RunOptions{{nullptr}},
                                  input_names, &input_tensor, 1,
                                  output_names, 1);
    
    // Get output
    float* output_data = outputs[0].GetTensorMutableData<float>();
    auto output_shape = outputs[0].GetTensorTypeAndShapeInfo().GetShape();
    
    size_t output_size = 1;
    for (auto dim : output_shape) output_size *= dim;
    
    std::vector<float> output(output_data, output_data + output_size);
    
    return postprocess(output, image.cols, image.rows);
}}'''
        
        return "// Raw buffer mode - implement based on your needs"
    
    def _build_postprocess_code(self) -> str:
        """Build postprocessing code based on config."""
        post = self.config.postprocess
        
        # YOLOv8 style postprocessing
        return f'''std::vector<Detection> Detector::postprocess(
    const std::vector<float>& output,
    int orig_width, int orig_height) {{
    
    std::vector<Detection> detections;
    
    // YOLOv8 output: [1, 84, 8400] → transposed to [8400, 84]
    // Format: [x, y, w, h, class_scores...]
    const int num_detections = 8400;
    const int num_outputs = 84;  // 4 + NUM_CLASSES
    
    // Calculate scale factors for letterbox
    float scale = std::min(float(INPUT_WIDTH) / orig_width,
                           float(INPUT_HEIGHT) / orig_height);
    int dx = (INPUT_WIDTH - int(orig_width * scale)) / 2;
    int dy = (INPUT_HEIGHT - int(orig_height * scale)) / 2;
    
    for (int i = 0; i < num_detections; ++i) {{
        // Get class scores
        float max_score = 0.0f;
        int max_class = 0;
        
        for (int c = 0; c < NUM_CLASSES; ++c) {{
            float score = output[i + (4 + c) * num_detections];
            if (score > max_score) {{
                max_score = score;
                max_class = c;
            }}
        }}
        
        if (max_score < CONF_THRESHOLD) continue;
        
        // Get box (cxcywh format)
        float cx = output[i + 0 * num_detections];
        float cy = output[i + 1 * num_detections];
        float w = output[i + 2 * num_detections];
        float h = output[i + 3 * num_detections];
        
        // Convert to xyxy
        float x1 = cx - w / 2;
        float y1 = cy - h / 2;
        float x2 = cx + w / 2;
        float y2 = cy + h / 2;
        
        // Scale back to original image
        x1 = (x1 - dx) / scale;
        y1 = (y1 - dy) / scale;
        x2 = (x2 - dx) / scale;
        y2 = (y2 - dy) / scale;
        
        // Clip to image bounds
        x1 = std::max(0.0f, std::min(x1, float(orig_width)));
        y1 = std::max(0.0f, std::min(y1, float(orig_height)));
        x2 = std::max(0.0f, std::min(x2, float(orig_width)));
        y2 = std::max(0.0f, std::min(y2, float(orig_height)));
        
        Detection det;
        det.x1 = x1;
        det.y1 = y1;
        det.x2 = x2;
        det.y2 = y2;
        det.confidence = max_score;
        det.class_id = max_class;
        det.class_name = (max_class < class_names_.size()) ? 
                         class_names_[max_class] : std::to_string(max_class);
        
        detections.push_back(det);
    }}
    
    // Apply NMS
    return nms(detections, IOU_THRESHOLD);
}}'''
    
    def _render_verify_single(self, mode: ImageInputMode) -> str:
        """Render verify_single.cpp template."""
        return f'''// verify_single.cpp - Auto-generated by ONNX CodeGen
// Usage: ./verify_single <model.onnx> <image.jpg> [labels.txt]

#include "detector.hpp"
#include <iostream>
#include <fstream>

std::vector<std::string> load_labels(const std::string& path) {{
    std::vector<std::string> labels;
    std::ifstream file(path);
    std::string line;
    while (std::getline(file, line)) {{
        if (!line.empty()) labels.push_back(line);
    }}
    return labels;
}}

int main(int argc, char* argv[]) {{
    if (argc < 3) {{
        std::cerr << "Usage: " << argv[0] << " <model.onnx> <image.jpg> [labels.txt]" << std::endl;
        return 1;
    }}
    
    std::string model_path = argv[1];
    std::string image_path = argv[2];
    std::vector<std::string> labels;
    
    if (argc > 3) {{
        labels = load_labels(argv[3]);
    }}
    
    // Load image
    cv::Mat image = cv::imread(image_path);
    if (image.empty()) {{
        std::cerr << "Error: Cannot load image " << image_path << std::endl;
        return 1;
    }}
    
    // Create detector
    Detector detector(model_path, labels);
    
    // Run detection
    auto start = std::chrono::high_resolution_clock::now();
    auto detections = detector.detect(image);
    auto end = std::chrono::high_resolution_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    std::cout << "Inference time: " << duration.count() << " ms" << std::endl;
    std::cout << "Detections: " << detections.size() << std::endl;
    
    // Draw results
    for (const auto& det : detections) {{
        cv::rectangle(image, 
                      cv::Point(det.x1, det.y1),
                      cv::Point(det.x2, det.y2),
                      cv::Scalar(0, 255, 0), 2);
        
        std::string label = det.class_name + " " + 
                           std::to_string(int(det.confidence * 100)) + "%";
        cv::putText(image, label, 
                    cv::Point(det.x1, det.y1 - 5),
                    cv::FONT_HERSHEY_SIMPLEX, 0.5,
                    cv::Scalar(0, 255, 0), 2);
        
        std::cout << det.class_name << " " << det.confidence 
                  << " [" << det.x1 << ", " << det.y1 
                  << ", " << det.x2 << ", " << det.y2 << "]" << std::endl;
    }}
    
    // Save result
    std::string output_path = image_path.substr(0, image_path.rfind('.')) + "_result.jpg";
    cv::imwrite(output_path, image);
    std::cout << "Result saved to: " << output_path << std::endl;
    
    // Save YOLO format
    std::string txt_path = image_path.substr(0, image_path.rfind('.')) + "_result.txt";
    std::ofstream txt_file(txt_path);
    for (const auto& det : detections) {{
        float cx = (det.x1 + det.x2) / 2 / image.cols;
        float cy = (det.y1 + det.y2) / 2 / image.rows;
        float w = (det.x2 - det.x1) / image.cols;
        float h = (det.y2 - det.y1) / image.rows;
        txt_file << det.class_id << " " << cx << " " << cy << " " << w << " " << h << std::endl;
    }}
    std::cout << "YOLO format saved to: " << txt_path << std::endl;
    
    return 0;
}}
'''
    
    def _render_cmake(self, mode: ImageInputMode) -> str:
        """Render CMakeLists.txt template."""
        opencv_find = "find_package(OpenCV REQUIRED)" if mode == ImageInputMode.OPENCV else ""
        opencv_link = "${OpenCV_LIBS}" if mode == ImageInputMode.OPENCV else ""
        
        return f'''# CMakeLists.txt - Auto-generated by ONNX CodeGen
cmake_minimum_required(VERSION 3.18)
project(detector)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find packages
{opencv_find}
find_package(onnxruntime REQUIRED)

# Add executable
add_executable(verify_single
    detector.cpp
    verify_single.cpp
)

# Include directories
target_include_directories(verify_single PRIVATE
    ${{CMAKE_CURRENT_SOURCE_DIR}}
    ${{onnxruntime_INCLUDE_DIRS}}
)

# Link libraries
target_link_libraries(verify_single
    {opencv_link}
    onnxruntime
)
'''
    
    def _render_readme(self, mode: ImageInputMode) -> str:
        """Render README.md template."""
        return f'''# ONNX Detector - Auto-generated

## Model Info
- Input: {self.config.preprocess.input_width}x{self.config.preprocess.input_height}
- Color: {self.config.preprocess.color_format.value.upper()}
- Classes: {self.config.postprocess.num_classes}

## Build

```bash
mkdir build && cd build
cmake ..
make
```

## Usage

```bash
./verify_single model.onnx test.jpg labels.txt
```

## Output
- `test_result.jpg` - Image with bounding boxes
- `test_result.txt` - YOLO format detections
'''
    
    # Placeholder methods for Android/iOS - implement similar to above
    def _render_android_jni(self) -> str:
        return "// Android JNI - see Section 8 in spec for full implementation"
    
    def _render_android_cmake(self) -> str:
        return "# Android CMakeLists.txt - see Section 8 in spec"
    
    def _render_kotlin_detector(self) -> str:
        return "// Detector.kt - see Section 8 in spec"
    
    def _render_kotlin_verify_single(self) -> str:
        return "// SingleImageVerifier.kt - see Section 8 in spec"
    
    def _render_kotlin_verify_folder(self) -> str:
        return "// BatchVerifier.kt - see Section 8 in spec"
    
    def _render_kotlin_camera(self) -> str:
        return "// CameraFrameAnalyzer.kt - see Section 8 in spec"
    
    def _render_android_readme(self, use_case: UseCase) -> str:
        return "# Android Integration - see Section 8 in spec"
    
    def _render_ios_bridge_h(self) -> str:
        return "// DetectorBridge.h - see Section 9 in spec"
    
    def _render_ios_bridge_mm(self) -> str:
        return "// DetectorBridge.mm - see Section 9 in spec"
    
    def _render_swift_detector(self) -> str:
        return "// Detector.swift - see Section 9 in spec"
    
    def _render_swift_verify_single(self) -> str:
        return "// SingleImageVerifier.swift - see Section 9 in spec"
    
    def _render_swift_verify_folder(self) -> str:
        return "// BatchVerifier.swift - see Section 9 in spec"
    
    def _render_swift_camera(self) -> str:
        return "// CameraFrameProcessor.swift - see Section 9 in spec"
    
    def _render_ios_readme(self, use_case: UseCase) -> str:
        return "# iOS Integration - see Section 9 in spec"
    
    # Stub methods for other modes
    def _generate_pc_stb(self, output_dir, result, callback):
        """Generate PC code with stb_image."""
        pass  # Similar to _generate_pc_opencv
    
    def _generate_pc_raw(self, output_dir, result, callback):
        """Generate PC code with raw buffer."""
        pass  # Similar to _generate_pc_opencv
```

### 6.11. Verifier Module

Module to verify Python code (user-provided) and C++ code (tool-generated).

```python
# core/verifier.py

import os
import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum
import re
import time


class VerificationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class Detection:
    """Detection result for comparison."""
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int
    class_name: str = ""


@dataclass
class VerificationResult:
    """Results verification."""
    status: VerificationStatus
    detections: List[Detection] = field(default_factory=list)
    timing_ms: float = 0.0
    output_image_path: Optional[str] = None
    error_message: str = ""
    stdout: str = ""
    stderr: str = ""


@dataclass
class ComparisonResult:
    """Python vs C++ comparison results."""
    match: bool
    python_result: VerificationResult
    cpp_result: VerificationResult
    matched_pairs: int = 0
    summary: str = ""


class PythonVerifier:
    """Verify Python inference code."""
    
    def __init__(self, python_code_path: str, model_path: str):
        self.python_code_path = Path(python_code_path)
        self.model_path = Path(model_path)
    
    def verify(self, test_image_path: str, timeout: int = 60) -> VerificationResult:
        """Run Python code with test image."""
        result = VerificationResult(status=VerificationStatus.RUNNING)
        
        try:
            cmd = ["python", str(self.python_code_path), str(self.model_path), test_image_path]
            
            start = time.time()
            proc = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=timeout, cwd=str(self.python_code_path.parent))
            result.timing_ms = (time.time() - start) * 1000
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            
            if proc.returncode != 0:
                result.status = VerificationStatus.FAILED
                result.error_message = f"Exit code {proc.returncode}"
                return result
            
            result.detections = self._parse_detections(proc.stdout)
            result.status = VerificationStatus.PASSED
            
        except subprocess.TimeoutExpired:
            result.status = VerificationStatus.ERROR
            result.error_message = f"Timeout after {timeout}s"
        except Exception as e:
            result.status = VerificationStatus.ERROR
            result.error_message = str(e)
        
        return result
    
    def _parse_detections(self, stdout: str) -> List[Detection]:
        """Parse detections from stdout. Format: class_name conf [x1, y1, x2, y2]"""
        detections = []
        pattern = re.compile(r"(\w+)\s+([\d.]+)\s*\[([\d.,\s]+)\]")
        
        for line in stdout.split('\n'):
            match = pattern.search(line)
            if match:
                coords = [float(x.strip()) for x in match.group(3).split(',')]
                if len(coords) >= 4:
                    detections.append(Detection(
                        x1=coords[0], y1=coords[1], x2=coords[2], y2=coords[3],
                        confidence=float(match.group(2)), class_id=0, class_name=match.group(1)
                    ))
        return detections


class CppVerifier:
    """Verify C++ generated code. Compile and run."""
    
    def __init__(self, cpp_dir: str, model_path: str):
        self.cpp_dir = Path(cpp_dir)
        self.model_path = Path(model_path)
        self.build_dir = self.cpp_dir / "build"
    
    def verify(self, test_image_path: str, labels_path: Optional[str] = None,
               timeout: int = 120) -> VerificationResult:
        """Compile and run C++ code."""
        result = VerificationResult(status=VerificationStatus.RUNNING)
        
        try:
            # Compile
            ok, msg = self._compile(timeout=timeout//2)
            if not ok:
                result.status = VerificationStatus.FAILED
                result.error_message = f"Compile failed: {msg}"
                return result
            
            # Run
            return self._run(test_image_path, labels_path, timeout=timeout//2)
            
        except Exception as e:
            result.status = VerificationStatus.ERROR
            result.error_message = str(e)
        return result
    
    def _compile(self, timeout: int = 60) -> Tuple[bool, str]:
        """Compile with CMake."""
        try:
            self.build_dir.mkdir(exist_ok=True)
            
            # cmake
            r1 = subprocess.run(["cmake", ".."], capture_output=True, text=True,
                               timeout=timeout, cwd=str(self.build_dir))
            if r1.returncode != 0:
                return False, r1.stderr
            
            # make
            r2 = subprocess.run(["make", "-j4"], capture_output=True, text=True,
                               timeout=timeout, cwd=str(self.build_dir))
            if r2.returncode != 0:
                return False, r2.stderr
            
            return True, "OK"
        except subprocess.TimeoutExpired:
            return False, "Compile timeout"
        except Exception as e:
            return False, str(e)
    
    def _run(self, test_image_path: str, labels_path: Optional[str],
             timeout: int = 60) -> VerificationResult:
        """Run executable."""
        result = VerificationResult(status=VerificationStatus.RUNNING)
        
        exe = self.build_dir / "verify_single"
        if not exe.exists():
            result.status = VerificationStatus.ERROR
            result.error_message = f"Executable not found"
            return result
        
        cmd = [str(exe), str(self.model_path), test_image_path]
        if labels_path:
            cmd.append(labels_path)
        
        try:
            start = time.time()
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            result.timing_ms = (time.time() - start) * 1000
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            
            if proc.returncode != 0:
                result.status = VerificationStatus.FAILED
                result.error_message = f"Exit code {proc.returncode}"
                return result
            
            result.detections = self._parse_detections(proc.stdout)
            result.status = VerificationStatus.PASSED
            
        except subprocess.TimeoutExpired:
            result.status = VerificationStatus.ERROR
            result.error_message = f"Timeout"
        
        return result
    
    def _parse_detections(self, stdout: str) -> List[Detection]:
        """Parse detections from stdout."""
        detections = []
        pattern = re.compile(r"(\w+)\s+([\d.]+)\s*\[([\d.,\s]+)\]")
        for line in stdout.split('\n'):
            match = pattern.search(line)
            if match:
                coords = [float(x.strip()) for x in match.group(3).split(',')]
                if len(coords) >= 4:
                    detections.append(Detection(
                        x1=coords[0], y1=coords[1], x2=coords[2], y2=coords[3],
                        confidence=float(match.group(2)), class_id=0, class_name=match.group(1)
                    ))
        return detections


class ResultComparator:
    """Compare Python vs C++ results."""
    
    def __init__(self, iou_threshold: float = 0.5, conf_tolerance: float = 0.05):
        self.iou_threshold = iou_threshold
        self.conf_tolerance = conf_tolerance
    
    def compare(self, py_result: VerificationResult, cpp_result: VerificationResult) -> ComparisonResult:
        """Compare results."""
        result = ComparisonResult(match=False, python_result=py_result, cpp_result=cpp_result)
        
        if py_result.status != VerificationStatus.PASSED:
            result.summary = f"Python failed: {py_result.error_message}"
            return result
        if cpp_result.status != VerificationStatus.PASSED:
            result.summary = f"C++ failed: {cpp_result.error_message}"
            return result
        
        py_dets, cpp_dets = py_result.detections, cpp_result.detections
        
        # Match detections by IoU
        matched_cpp = set()
        matched_count = 0
        
        for py_det in py_dets:
            for j, cpp_det in enumerate(cpp_dets):
                if j in matched_cpp or py_det.class_name != cpp_det.class_name:
                    continue
                iou = self._calc_iou(py_det, cpp_det)
                if iou >= self.iou_threshold:
                    matched_cpp.add(j)
                    matched_count += 1
                    break
        
        result.matched_pairs = matched_count
        total = max(len(py_dets), len(cpp_dets))
        
        if total == 0:
            result.match = True
            result.summary = "Both have 0 detections - MATCH"
        elif matched_count / total >= 0.8:
            result.match = True
            result.summary = f"MATCH: {matched_count}/{total} detections matched"
        else:
            result.summary = f"MISMATCH: {matched_count}/{total} matched"
        
        return result
    
    def _calc_iou(self, a: Detection, b: Detection) -> float:
        """Calculate IoU between two boxes."""
        x1, y1 = max(a.x1, b.x1), max(a.y1, b.y1)
        x2, y2 = min(a.x2, b.x2), min(a.y2, b.y2)
        inter = max(0, x2-x1) * max(0, y2-y1)
        area_a = (a.x2-a.x1) * (a.y2-a.y1)
        area_b = (b.x2-b.x1) * (b.y2-b.y1)
        return inter / (area_a + area_b - inter) if (area_a + area_b - inter) > 0 else 0


class VerificationOrchestrator:
    """Orchestrator to run full verification flow."""
    
    def __init__(self, model_path: str, cpp_dir: str, python_code_path: Optional[str] = None):
        self.model_path = model_path
        self.cpp_dir = cpp_dir
        self.python_code_path = python_code_path
    
    def run_full_verification(self, test_image_path: str, labels_path: Optional[str] = None,
                              verify_python: bool = True, verify_cpp: bool = True,
                              progress_callback=None) -> ComparisonResult:
        """Run full verification: Python → C++ → Compare."""
        
        py_result = VerificationResult(status=VerificationStatus.SKIPPED)
        cpp_result = VerificationResult(status=VerificationStatus.SKIPPED)
        
        # Step 1: Verify Python (if available and requested)
        if verify_python and self.python_code_path:
            if progress_callback:
                progress_callback(10, "Verifying Python code...")
            verifier = PythonVerifier(self.python_code_path, self.model_path)
            py_result = verifier.verify(test_image_path)
        
        # Step 2: Verify C++
        if verify_cpp:
            if progress_callback:
                progress_callback(50, "Compiling and verifying C++ code...")
            verifier = CppVerifier(self.cpp_dir, self.model_path)
            cpp_result = verifier.verify(test_image_path, labels_path)
        
        # Step 3: Compare
        if progress_callback:
            progress_callback(90, "Comparing results...")
        
        comparator = ResultComparator()
        comparison = comparator.compare(py_result, cpp_result)
        
        if progress_callback:
            progress_callback(100, "Verification complete!")
        
        return comparison
```

---

## 7. Generated C++ Code - Core (PC/Desktop)

This section contains C++ code for PC/Desktop. Tool generates code to verify 1 image, users can extend if needed.

### 7.1. Use Cases and Output Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  USE CASES VÀ CODE TARGETS                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Platform │ Use Case              │ Output                      │
│  ─────────┼───────────────────────┼───────────────────────────  │
│  PC       │ Verify single image          │ image + YOLO txt            │
│  Android  │ Verify single image          │ image + YOLO txt            │
│  Android  │ Verify folder        │ images + YOLO txts          │
│  Android  │ Camera integration    │ detections only             │
│  iOS      │ Verify single image          │ image + YOLO txt            │
│  iOS      │ Verify folder        │ images + YOLO txts          │
│  iOS      │ Camera integration    │ detections only             │
│                                                                 │
│  PC:      Tool generates code to verify 1 image.                         │
│           User tự mở rộng cho batch/video if needed.             │
│                                                                 │
│  Mobile:  User chooses 1 of 3 options.                         │
│           Tool generates corresponding code.                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2. PC Generated Files

```
┌─────────────────────────────────────────────────────────────────┐
│  PC OUTPUT FILES                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📁 output/                                                     │
│  ├── detector.hpp              # Core detector class           │
│  ├── detector.cpp              # Implementation                │
│  ├── verify_single.cpp         # main(): verify 1 image        │
│  ├── CMakeLists.txt            # Build configuration           │
│  └── README.md                 # Instructions build & mở rộng     │
│                                                                 │
│  USAGE:                                                         │
│  $ mkdir build && cd build                                     │
│  $ cmake .. && make                                            │
│  $ ./verify_single ../model.onnx ../test.jpg                   │
│                                                                 │
│  OUTPUT:                                                        │
│  • Console: detection results                                  │
│  • test_result.jpg: image with bounding boxes                    │
│  • test_result.txt: YOLO format results                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3. Image Library Options

```
┌─────────────────────────────────────────────────────────────────┐
│  PC IMAGE LIBRARY OPTIONS                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  OPTION A: OpenCV (Recommended)                                │
│  ─────────────────────────────                                  │
│  • Full-featured image I/O                                     │
│  • Drawing utilities (rectangles, text)                        │
│  • Easy to extend for video/webcam                            │
│  • Dependency: ~50MB                                           │
│                                                                 │
│  OPTION B: stb_image (Lightweight)                             │
│  ─────────────────────────────────                              │
│  • Header-only, bundled with output                           │
│  • Basic image loading (JPG, PNG)                             │
│  • No drawing utils (results saved as text only)              │
│  • Dependency: ~100KB (single header)                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.4. Mode 1: OpenCV

```cpp
// detector_opencv.hpp

#pragma once
#include <opencv2/opencv.hpp>
#include <onnxruntime_cxx_api.h>
#include <vector>
#include <string>

namespace detector {

struct Detection {
    cv::Rect box;
    float confidence;
    int class_id;
    std::string label;
};

class Detector {
public:
    Detector(const std::string& model_path,
             float conf_threshold = 0.25f,
             float iou_threshold = 0.45f);
    
    // OpenCV Mat interface
    std::vector<Detection> detect(const cv::Mat& image);
    
    // Load from file
    std::vector<Detection> detectFromFile(const std::string& image_path);

private:
    std::vector<float> preprocess(const cv::Mat& image);
    std::vector<Detection> postprocess(const std::vector<float>& output,
                                        int orig_width, int orig_height);
    
    std::unique_ptr<Ort::Env> env_;
    std::unique_ptr<Ort::Session> session_;
    
    int input_width_ = {INPUT_WIDTH};
    int input_height_ = {INPUT_HEIGHT};
    float conf_threshold_;
    float iou_threshold_;
};

} // namespace detector
```

```cpp
// detector_opencv.cpp

#include "detector_opencv.hpp"

namespace detector {

Detector::Detector(const std::string& model_path,
                   float conf_threshold,
                   float iou_threshold)
    : conf_threshold_(conf_threshold), iou_threshold_(iou_threshold) {
    
    env_ = std::make_unique<Ort::Env>(ORT_LOGGING_LEVEL_WARNING, "Detector");
    Ort::SessionOptions options;
    options.SetIntraOpNumThreads(4);
    session_ = std::make_unique<Ort::Session>(*env_, model_path.c_str(), options);
}

std::vector<Detection> Detector::detect(const cv::Mat& image) {
    if (image.empty()) return {};
    
    int orig_w = image.cols;
    int orig_h = image.rows;
    
    auto input_tensor = preprocess(image);
    
    // Run inference...
    // (ONNX Runtime code)
    
    return postprocess(output, orig_w, orig_h);
}

std::vector<Detection> Detector::detectFromFile(const std::string& image_path) {
    cv::Mat image = cv::imread(image_path);
    if (image.empty()) {
        throw std::runtime_error("Failed to load image: " + image_path);
    }
    return detect(image);
}

std::vector<float> Detector::preprocess(const cv::Mat& image) {
    cv::Mat processed;
    
    // Resize (letterbox)
    float scale = std::min(
        static_cast<float>(input_width_) / image.cols,
        static_cast<float>(input_height_) / image.rows
    );
    
    int new_w = static_cast<int>(image.cols * scale);
    int new_h = static_cast<int>(image.rows * scale);
    
    cv::resize(image, processed, cv::Size(new_w, new_h));
    
    // Padding
    int pad_w = (input_width_ - new_w) / 2;
    int pad_h = (input_height_ - new_h) / 2;
    cv::copyMakeBorder(processed, processed,
                       pad_h, input_height_ - new_h - pad_h,
                       pad_w, input_width_ - new_w - pad_w,
                       cv::BORDER_CONSTANT, cv::Scalar(114, 114, 114));
    
    // BGR to RGB
    cv::cvtColor(processed, processed, cv::COLOR_BGR2RGB);
    
    // Normalize and convert to CHW
    processed.convertTo(processed, CV_32F, 1.0f / 255.0f);
    
    std::vector<cv::Mat> channels(3);
    cv::split(processed, channels);
    
    std::vector<float> tensor;
    tensor.reserve(3 * input_height_ * input_width_);
    for (const auto& ch : channels) {
        tensor.insert(tensor.end(), ch.begin<float>(), ch.end<float>());
    }
    
    return tensor;
}

} // namespace detector
```

### 7.4.1. PC: verify_single.cpp

```cpp
// verify_single.cpp
// Verify detection on 1 image, output YOLO format

#include "detector.hpp"
#include <opencv2/opencv.hpp>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <chrono>

// Color palette for visualization
const std::vector<cv::Scalar> COLORS = {
    {0, 0, 255},    // Red
    {0, 255, 0},    // Green
    {255, 0, 0},    // Blue
    {0, 255, 255},  // Yellow
    {255, 255, 0},  // Cyan
    {255, 0, 255},  // Magenta
    {0, 128, 255}   // Orange
};

// Load class labels from file
std::vector<std::string> loadLabels(const std::string& path) {
    std::vector<std::string> labels;
    std::ifstream file(path);
    if (file.is_open()) {
        std::string line;
        while (std::getline(file, line)) {
            if (!line.empty()) {
                labels.push_back(line);
            }
        }
    }
    return labels;
}

// Get filename without extension
std::string getBaseName(const std::string& path) {
    size_t lastSlash = path.find_last_of("/\\");
    std::string filename = (lastSlash != std::string::npos) ? path.substr(lastSlash + 1) : path;
    size_t lastDot = filename.find_last_of('.');
    return (lastDot != std::string::npos) ? filename.substr(0, lastDot) : filename;
}

// Save detections in YOLO format
void saveYoloFormat(
    const std::vector<detector::Detection>& detections,
    int imgWidth, int imgHeight,
    const std::string& outputPath
) {
    std::ofstream file(outputPath);
    if (!file.is_open()) {
        std::cerr << "Error: Cannot create output file: " << outputPath << std::endl;
        return;
    }
    
    file << std::fixed << std::setprecision(6);
    for (const auto& det : detections) {
        double xCenter = (det.box.x + det.box.width / 2.0) / imgWidth;
        double yCenter = (det.box.y + det.box.height / 2.0) / imgHeight;
        double w = static_cast<double>(det.box.width) / imgWidth;
        double h = static_cast<double>(det.box.height) / imgHeight;
        
        file << det.class_id << " "
             << xCenter << " " << yCenter << " "
             << w << " " << h << " "
             << std::setprecision(4) << det.confidence << "\n";
    }
}

// Draw detections on image
void drawDetections(
    cv::Mat& image,
    const std::vector<detector::Detection>& detections,
    const std::vector<std::string>& labels
) {
    for (const auto& det : detections) {
        cv::Scalar color = COLORS[det.class_id % COLORS.size()];
        
        // Draw bounding box
        cv::rectangle(image, det.box, color, 2);
        
        // Create label
        std::string label = (det.class_id < labels.size()) 
            ? labels[det.class_id] 
            : std::to_string(det.class_id);
        label += " " + std::to_string(det.confidence).substr(0, 4);
        
        // Draw label background
        int baseline;
        cv::Size labelSize = cv::getTextSize(label, cv::FONT_HERSHEY_SIMPLEX, 0.6, 1, &baseline);
        cv::rectangle(
            image,
            cv::Point(det.box.x, det.box.y - labelSize.height - 10),
            cv::Point(det.box.x + labelSize.width + 6, det.box.y),
            color, cv::FILLED
        );
        
        // Draw label text
        cv::putText(
            image, label,
            cv::Point(det.box.x + 3, det.box.y - 5),
            cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 255, 255), 1
        );
    }
}

void printUsage(const char* programName) {
    std::cout << "Usage: " << programName << " <model.onnx> <image> [labels.txt]\n"
              << "\n"
              << "Arguments:\n"
              << "  model.onnx    Path to ONNX model file\n"
              << "  image         Path to input image (jpg, png, etc.)\n"
              << "  labels.txt    (Optional) Path to class labels file\n"
              << "\n"
              << "Output:\n"
              << "  <image>_result.jpg    Image with bounding boxes\n"
              << "  <image>_result.txt    Detection results in YOLO format\n"
              << std::endl;
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        printUsage(argv[0]);
        return 1;
    }
    
    std::string modelPath = argv[1];
    std::string imagePath = argv[2];
    std::string labelsPath = (argc > 3) ? argv[3] : "";
    
    // Load labels
    std::vector<std::string> labels;
    if (!labelsPath.empty()) {
        labels = loadLabels(labelsPath);
        std::cout << "Loaded " << labels.size() << " labels" << std::endl;
    }
    
    // Load image
    cv::Mat image = cv::imread(imagePath);
    if (image.empty()) {
        std::cerr << "Error: Cannot load image: " << imagePath << std::endl;
        return 1;
    }
    std::cout << "Image size: " << image.cols << "x" << image.rows << std::endl;
    
    // Initialize detector
    std::cout << "Loading model: " << modelPath << std::endl;
    detector::Detector det(modelPath);
    
    // Run detection
    std::cout << "Running inference..." << std::endl;
    auto start = std::chrono::high_resolution_clock::now();
    
    auto detections = det.detect(image);
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    std::cout << "Found " << detections.size() << " objects in " << duration.count() << " ms" << std::endl;
    
    // Print detections
    std::cout << "\nDetections:" << std::endl;
    for (const auto& d : detections) {
        std::string label = (d.class_id < labels.size()) ? labels[d.class_id] : std::to_string(d.class_id);
        std::cout << "  " << label << ": " << std::fixed << std::setprecision(2) 
                  << (d.confidence * 100) << "% at ["
                  << d.box.x << ", " << d.box.y << ", "
                  << d.box.width << ", " << d.box.height << "]" << std::endl;
    }
    
    // Save output files
    std::string baseName = getBaseName(imagePath);
    
    // Draw and save image with detections
    cv::Mat outputImage = image.clone();
    drawDetections(outputImage, detections, labels);
    std::string outputImagePath = baseName + "_result.jpg";
    cv::imwrite(outputImagePath, outputImage);
    std::cout << "\nSaved: " << outputImagePath << std::endl;
    
    // Save YOLO format results
    std::string outputYoloPath = baseName + "_result.txt";
    saveYoloFormat(detections, image.cols, image.rows, outputYoloPath);
    std::cout << "Saved: " << outputYoloPath << std::endl;
    
    return 0;
}
```

### 7.4.2. PC: CMakeLists.txt

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.18)
project(detector)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find packages
find_package(OpenCV REQUIRED)
find_package(onnxruntime QUIET)

# If onnxruntime not found via CMake, try pkg-config or manual path
if(NOT onnxruntime_FOUND)
    # Try pkg-config
    find_package(PkgConfig)
    if(PkgConfig_FOUND)
        pkg_check_modules(ONNXRUNTIME onnxruntime)
    endif()
    
    # Manual fallback
    if(NOT ONNXRUNTIME_FOUND)
        # User should set ONNXRUNTIME_ROOT environment variable
        set(ONNXRUNTIME_ROOT $ENV{ONNXRUNTIME_ROOT})
        if(ONNXRUNTIME_ROOT)
            set(ONNXRUNTIME_INCLUDE_DIRS "${ONNXRUNTIME_ROOT}/include")
            set(ONNXRUNTIME_LIBRARY_DIRS "${ONNXRUNTIME_ROOT}/lib")
            find_library(ONNXRUNTIME_LIBRARIES onnxruntime PATHS ${ONNXRUNTIME_LIBRARY_DIRS})
        else()
            message(FATAL_ERROR "ONNX Runtime not found. Please set ONNXRUNTIME_ROOT environment variable.")
        endif()
    endif()
endif()

# Include directories
include_directories(${OpenCV_INCLUDE_DIRS})
include_directories(${ONNXRUNTIME_INCLUDE_DIRS})
link_directories(${ONNXRUNTIME_LIBRARY_DIRS})

# Build detector library
add_library(detector_lib STATIC
    detector.hpp
    detector.cpp
)
target_link_libraries(detector_lib
    ${OpenCV_LIBS}
    ${ONNXRUNTIME_LIBRARIES}
)

# Build verify_single executable
add_executable(verify_single
    verify_single.cpp
)
target_link_libraries(verify_single
    detector_lib
    ${OpenCV_LIBS}
)

# Install
install(TARGETS verify_single DESTINATION bin)
install(FILES detector.hpp DESTINATION include)
```

### 7.4.3. PC: README.md (Template)

**This file is generated with code, guides user to build and extend:**

```text
================================================================================
                         OBJECT DETECTOR - PC VERSION
================================================================================

BUILD REQUIREMENTS
------------------
- CMake >= 3.18
- C++17 compatible compiler
- OpenCV 4.x
- ONNX Runtime C++ libraries

INSTALLATION
------------
Ubuntu/Debian:
    sudo apt install cmake build-essential libopencv-dev
    # ONNX Runtime: download from https://github.com/microsoft/onnxruntime/releases
    export ONNXRUNTIME_ROOT=/path/to/onnxruntime

macOS:
    brew install cmake opencv onnxruntime

Windows:
    - Install Visual Studio 2019+
    - Download OpenCV and ONNX Runtime
    - Set ONNXRUNTIME_ROOT environment variable

BUILD
-----
    mkdir build && cd build
    cmake ..
    make

USAGE
-----
    # Basic usage
    ./verify_single model.onnx image.jpg

    # With labels file  
    ./verify_single model.onnx image.jpg labels.txt

OUTPUT FILES
------------
- <image>_result.jpg  : Image with drawn bounding boxes
- <image>_result.txt  : Detection results in YOLO format

YOLO FORMAT
-----------
Each line: <class_id> <x_center> <y_center> <width> <height> <confidence>
All coordinates normalized to [0,1].

EXTENDING FOR BATCH/VIDEO
-------------------------
See code examples below for extending to process folders or video streams.
```

**Batch Processing Example (C++):**

```cpp
#include <filesystem>
namespace fs = std::filesystem;

for (const auto& entry : fs::directory_iterator("images/")) {
    if (entry.path().extension() == ".jpg") {
        cv::Mat image = cv::imread(entry.path());
        auto detections = detector.detect(image);
        // Process results...
    }
}
```

**Video Processing Example (C++):**

```cpp
cv::VideoCapture cap("video.mp4");
// Or webcam: cv::VideoCapture cap(0);

cv::Mat frame;
while (cap.read(frame)) {
    auto detections = detector.detect(frame);
    drawDetections(frame, detections, labels);
    cv::imshow("Detection", frame);
    if (cv::waitKey(1) == 27) break;  // ESC to quit
}
```

```cpp
// detector_raw.hpp

#pragma once
#include <onnxruntime_cxx_api.h>
#include <vector>
#include <cstdint>

namespace detector {

struct BoundingBox {
    int x, y, width, height;
    float confidence;
    int class_id;
};

/**
 * Raw buffer detector - no external image library dependencies.
 * 
 * Input: Raw pixel buffer (RGB or BGR, uint8_t, HWC format)
 * User is responsible for image loading and color conversion.
 */
class Detector {
public:
    Detector(const std::string& model_path,
             float conf_threshold = 0.25f,
             float iou_threshold = 0.45f);
    
    /**
     * Detect objects in raw pixel buffer.
     * 
     * @param pixels     Pointer to pixel data (HWC format, uint8_t)
     * @param width      Image width
     * @param height     Image height
     * @param channels   Number of channels (3 for RGB/BGR)
     * @param is_bgr     True if pixels are in BGR order, false for RGB
     * @return           Vector of detections
     */
    std::vector<BoundingBox> detect(
        const uint8_t* pixels,
        int width,
        int height,
        int channels = 3,
        bool is_bgr = false
    );

private:
    std::vector<float> preprocess(
        const uint8_t* pixels,
        int width, int height, int channels,
        bool is_bgr
    );
    
    // Simple resize implementation (bilinear)
    void resize_bilinear(
        const uint8_t* src, int src_w, int src_h,
        uint8_t* dst, int dst_w, int dst_h,
        int channels
    );
    
    std::vector<BoundingBox> postprocess(
        const std::vector<float>& output,
        int orig_width, int orig_height
    );
    
    std::unique_ptr<Ort::Env> env_;
    std::unique_ptr<Ort::Session> session_;
    
    int input_width_ = {INPUT_WIDTH};
    int input_height_ = {INPUT_HEIGHT};
    float conf_threshold_;
    float iou_threshold_;
    
    // Letterbox info for coordinate conversion
    float scale_;
    int pad_w_, pad_h_;
};

} // namespace detector
```

```cpp
// detector_raw.cpp

#include "detector_raw.hpp"
#include <algorithm>
#include <cmath>
#include <cstring>

namespace detector {

Detector::Detector(const std::string& model_path,
                   float conf_threshold,
                   float iou_threshold)
    : conf_threshold_(conf_threshold), iou_threshold_(iou_threshold) {
    
    env_ = std::make_unique<Ort::Env>(ORT_LOGGING_LEVEL_WARNING, "Detector");
    Ort::SessionOptions options;
    options.SetIntraOpNumThreads(4);
    session_ = std::make_unique<Ort::Session>(*env_, model_path.c_str(), options);
}

std::vector<BoundingBox> Detector::detect(
    const uint8_t* pixels,
    int width, int height, int channels,
    bool is_bgr
) {
    if (!pixels || width <= 0 || height <= 0) return {};
    
    auto input_tensor = preprocess(pixels, width, height, channels, is_bgr);
    
    // Run ONNX inference...
    // ...
    
    return postprocess(output, width, height);
}

void Detector::resize_bilinear(
    const uint8_t* src, int src_w, int src_h,
    uint8_t* dst, int dst_w, int dst_h,
    int channels
) {
    float x_ratio = static_cast<float>(src_w) / dst_w;
    float y_ratio = static_cast<float>(src_h) / dst_h;
    
    for (int y = 0; y < dst_h; ++y) {
        for (int x = 0; x < dst_w; ++x) {
            float src_x = x * x_ratio;
            float src_y = y * y_ratio;
            
            int x0 = static_cast<int>(src_x);
            int y0 = static_cast<int>(src_y);
            int x1 = std::min(x0 + 1, src_w - 1);
            int y1 = std::min(y0 + 1, src_h - 1);
            
            float x_diff = src_x - x0;
            float y_diff = src_y - y0;
            
            for (int c = 0; c < channels; ++c) {
                float top = src[(y0 * src_w + x0) * channels + c] * (1 - x_diff) +
                           src[(y0 * src_w + x1) * channels + c] * x_diff;
                float bottom = src[(y1 * src_w + x0) * channels + c] * (1 - x_diff) +
                              src[(y1 * src_w + x1) * channels + c] * x_diff;
                
                dst[(y * dst_w + x) * channels + c] =
                    static_cast<uint8_t>(top * (1 - y_diff) + bottom * y_diff);
            }
        }
    }
}

std::vector<float> Detector::preprocess(
    const uint8_t* pixels,
    int width, int height, int channels,
    bool is_bgr
) {
    // Calculate letterbox parameters
    scale_ = std::min(
        static_cast<float>(input_width_) / width,
        static_cast<float>(input_height_) / height
    );
    
    int new_w = static_cast<int>(width * scale_);
    int new_h = static_cast<int>(height * scale_);
    pad_w_ = (input_width_ - new_w) / 2;
    pad_h_ = (input_height_ - new_h) / 2;
    
    // Allocate resized buffer
    std::vector<uint8_t> resized(new_w * new_h * channels);
    resize_bilinear(pixels, width, height,
                    resized.data(), new_w, new_h, channels);
    
    // Create padded buffer
    std::vector<uint8_t> padded(input_width_ * input_height_ * channels, 114);
    
    // Copy resized image to center
    for (int y = 0; y < new_h; ++y) {
        std::memcpy(
            padded.data() + ((y + pad_h_) * input_width_ + pad_w_) * channels,
            resized.data() + y * new_w * channels,
            new_w * channels
        );
    }
    
    // Convert to float CHW format
    std::vector<float> tensor(3 * input_height_ * input_width_);
    
    for (int y = 0; y < input_height_; ++y) {
        for (int x = 0; x < input_width_; ++x) {
            int src_idx = (y * input_width_ + x) * channels;
            
            // Handle BGR vs RGB
            int r_src = is_bgr ? 2 : 0;
            int b_src = is_bgr ? 0 : 2;
            
            // CHW format: [C, H, W]
            int r_dst = 0 * input_height_ * input_width_ + y * input_width_ + x;
            int g_dst = 1 * input_height_ * input_width_ + y * input_width_ + x;
            int b_dst = 2 * input_height_ * input_width_ + y * input_width_ + x;
            
            tensor[r_dst] = padded[src_idx + r_src] / 255.0f;
            tensor[g_dst] = padded[src_idx + 1] / 255.0f;
            tensor[b_dst] = padded[src_idx + b_src] / 255.0f;
        }
    }
    
    return tensor;
}

} // namespace detector
```

---

## 8. Generated C++ Code - Android

This section contains C++ and Kotlin code specifically for Android platform.

### 8.1. Android Use Cases and Output Files

```
┌─────────────────────────────────────────────────────────────────┐
│  ANDROID: 3 USE CASES                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  OPTION 1: Verify single image                                        │
│  ──────────────────────                                         │
│  Purpose: Quick test on device                              │
│  Output: image + bboxes, result.txt (YOLO format)                │
│                                                                 │
│  📁 output/                                                     │
│  ├── cpp/                                                       │
│  │   ├── detector.hpp                                          │
│  │   ├── detector.cpp                                          │
│  │   ├── detector_jni.cpp                                      │
│  │   └── CMakeLists.txt                                        │
│  ├── kotlin/                                                    │
│  │   ├── Detector.kt              # JNI wrapper                │
│  │   └── SingleImageVerifier.kt   # Verify single image, save result │
│  └── README.md                                                  │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  OPTION 2: Verify image folder                                  │
│  ────────────────────────────                                   │
│  Purpose: Batch evaluation, calculate mAP                          │
│  Output: images + bboxes, results/*.txt (YOLO format)             │
│                                                                 │
│  📁 output/                                                     │
│  ├── cpp/                                                       │
│  │   ├── detector.hpp                                          │
│  │   ├── detector.cpp                                          │
│  │   ├── detector_jni.cpp                                      │
│  │   └── CMakeLists.txt                                        │
│  ├── kotlin/                                                    │
│  │   ├── Detector.kt                                           │
│  │   └── BatchVerifier.kt         # Loop folder, save results │
│  └── README.md                                                  │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  OPTION 3: Camera integration (Production)                     │
│  ─────────────────────────────────────────                      │
│  Purpose: Real-time detection from camera                       │
│  Output: None - only return detections for app to handle           │
│                                                                 │
│  📁 output/                                                     │
│  ├── cpp/                                                       │
│  │   ├── detector.hpp                                          │
│  │   ├── detector.cpp                                          │
│  │   ├── detector_jni.cpp                                      │
│  │   └── CMakeLists.txt                                        │
│  ├── kotlin/                                                    │
│  │   ├── Detector.kt                                           │
│  │   └── CameraFrameAnalyzer.kt   # CameraX ImageAnalysis     │
│  └── README.md                                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2. Android Native Detector (JNI + Bitmap)

```cpp
// detector_android.hpp

#pragma once
#include <jni.h>
#include <android/bitmap.h>
#include <onnxruntime_cxx_api.h>
#include <vector>
#include <memory>

namespace detector {

struct Detection {
    int x, y, width, height;
    float confidence;
    int class_id;
};

class Detector {
public:
    Detector(const std::string& model_path,
             float conf_threshold = 0.25f,
             float iou_threshold = 0.45f);
    
    /**
     * Detect from Android Bitmap via JNI.
     * 
     * @param env        JNI environment
     * @param bitmap     Android Bitmap object (ARGB_8888 or RGB_565)
     * @return           Vector of detections
     */
    std::vector<Detection> detectFromBitmap(JNIEnv* env, jobject bitmap);

private:
    std::vector<float> preprocessBitmap(
        void* pixels,
        int width, int height,
        AndroidBitmapFormat format
    );
    
    std::vector<Detection> postprocess(
        const std::vector<float>& output,
        int orig_width, int orig_height
    );
    
    std::unique_ptr<Ort::Env> env_;
    std::unique_ptr<Ort::Session> session_;
    
    int input_width_ = {INPUT_WIDTH};
    int input_height_ = {INPUT_HEIGHT};
    float conf_threshold_;
    float iou_threshold_;
    float scale_;
    int pad_w_, pad_h_;
};

} // namespace detector


// JNI Functions
extern "C" {

JNIEXPORT jlong JNICALL
Java_com_example_detector_NativeDetector_createDetector(
    JNIEnv* env,
    jobject thiz,
    jstring model_path,
    jfloat conf_threshold,
    jfloat iou_threshold
);

JNIEXPORT void JNICALL
Java_com_example_detector_NativeDetector_destroyDetector(
    JNIEnv* env,
    jobject thiz,
    jlong detector_ptr
);

JNIEXPORT jobjectArray JNICALL
Java_com_example_detector_NativeDetector_detect(
    JNIEnv* env,
    jobject thiz,
    jlong detector_ptr,
    jobject bitmap
);

}
```

```cpp
// detector_android.cpp

#include "detector_android.hpp"
#include <android/log.h>

#define LOG_TAG "ONNXDetector"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

namespace detector {

Detector::Detector(const std::string& model_path,
                   float conf_threshold,
                   float iou_threshold)
    : conf_threshold_(conf_threshold), iou_threshold_(iou_threshold) {
    
    env_ = std::make_unique<Ort::Env>(ORT_LOGGING_LEVEL_WARNING, "Detector");
    
    Ort::SessionOptions options;
    options.SetIntraOpNumThreads(4);
    
    // Enable NNAPI for Android acceleration
    // Ort::ThrowOnError(OrtSessionOptionsAppendExecutionProvider_Nnapi(options, 0));
    
    session_ = std::make_unique<Ort::Session>(*env_, model_path.c_str(), options);
    
    LOGI("Detector initialized with model: %s", model_path.c_str());
}

std::vector<Detection> Detector::detectFromBitmap(JNIEnv* jni_env, jobject bitmap) {
    AndroidBitmapInfo info;
    void* pixels = nullptr;
    
    // Get bitmap info
    if (AndroidBitmap_getInfo(jni_env, bitmap, &info) != ANDROID_BITMAP_RESULT_SUCCESS) {
        LOGE("Failed to get bitmap info");
        return {};
    }
    
    // Lock pixels
    if (AndroidBitmap_lockPixels(jni_env, bitmap, &pixels) != ANDROID_BITMAP_RESULT_SUCCESS) {
        LOGE("Failed to lock bitmap pixels");
        return {};
    }
    
    // Preprocess
    auto input_tensor = preprocessBitmap(pixels, info.width, info.height,
                                         static_cast<AndroidBitmapFormat>(info.format));
    
    // Unlock pixels
    AndroidBitmap_unlockPixels(jni_env, bitmap);
    
    // Run inference...
    // ...
    
    return postprocess(output, info.width, info.height);
}

std::vector<float> Detector::preprocessBitmap(
    void* pixels,
    int width, int height,
    AndroidBitmapFormat format
) {
    // Calculate letterbox
    scale_ = std::min(
        static_cast<float>(input_width_) / width,
        static_cast<float>(input_height_) / height
    );
    
    int new_w = static_cast<int>(width * scale_);
    int new_h = static_cast<int>(height * scale_);
    pad_w_ = (input_width_ - new_w) / 2;
    pad_h_ = (input_height_ - new_h) / 2;
    
    // Allocate output tensor
    std::vector<float> tensor(3 * input_height_ * input_width_, 114.0f / 255.0f);
    
    // Process based on bitmap format
    if (format == ANDROID_BITMAP_FORMAT_RGBA_8888) {
        uint32_t* src = static_cast<uint32_t*>(pixels);
        
        for (int y = 0; y < new_h; ++y) {
            for (int x = 0; x < new_w; ++x) {
                // Source coordinates (simple nearest neighbor resize)
                int src_x = static_cast<int>(x / scale_);
                int src_y = static_cast<int>(y / scale_);
                
                uint32_t pixel = src[src_y * width + src_x];
                
                // ARGB_8888: AARRGGBB
                uint8_t r = (pixel >> 16) & 0xFF;
                uint8_t g = (pixel >> 8) & 0xFF;
                uint8_t b = pixel & 0xFF;
                
                // Destination with padding
                int dst_y = y + pad_h_;
                int dst_x = x + pad_w_;
                
                // CHW format
                tensor[0 * input_height_ * input_width_ + dst_y * input_width_ + dst_x] = r / 255.0f;
                tensor[1 * input_height_ * input_width_ + dst_y * input_width_ + dst_x] = g / 255.0f;
                tensor[2 * input_height_ * input_width_ + dst_y * input_width_ + dst_x] = b / 255.0f;
            }
        }
    }
    else if (format == ANDROID_BITMAP_FORMAT_RGB_565) {
        uint16_t* src = static_cast<uint16_t*>(pixels);
        
        for (int y = 0; y < new_h; ++y) {
            for (int x = 0; x < new_w; ++x) {
                int src_x = static_cast<int>(x / scale_);
                int src_y = static_cast<int>(y / scale_);
                
                uint16_t pixel = src[src_y * width + src_x];
                
                // RGB_565: RRRRRGGGGGGBBBBB
                uint8_t r = ((pixel >> 11) & 0x1F) << 3;
                uint8_t g = ((pixel >> 5) & 0x3F) << 2;
                uint8_t b = (pixel & 0x1F) << 3;
                
                int dst_y = y + pad_h_;
                int dst_x = x + pad_w_;
                
                tensor[0 * input_height_ * input_width_ + dst_y * input_width_ + dst_x] = r / 255.0f;
                tensor[1 * input_height_ * input_width_ + dst_y * input_width_ + dst_x] = g / 255.0f;
                tensor[2 * input_height_ * input_width_ + dst_y * input_width_ + dst_x] = b / 255.0f;
            }
        }
    }
    
    return tensor;
}

} // namespace detector


// ─────────────────────────────────────────────────────────────────
// JNI Implementation
// ─────────────────────────────────────────────────────────────────

extern "C" {

JNIEXPORT jlong JNICALL
Java_com_example_detector_NativeDetector_createDetector(
    JNIEnv* env,
    jobject thiz,
    jstring model_path,
    jfloat conf_threshold,
    jfloat iou_threshold
) {
    const char* path = env->GetStringUTFChars(model_path, nullptr);
    
    auto* detector = new detector::Detector(path, conf_threshold, iou_threshold);
    
    env->ReleaseStringUTFChars(model_path, path);
    
    return reinterpret_cast<jlong>(detector);
}

JNIEXPORT void JNICALL
Java_com_example_detector_NativeDetector_destroyDetector(
    JNIEnv* env,
    jobject thiz,
    jlong detector_ptr
) {
    auto* detector = reinterpret_cast<detector::Detector*>(detector_ptr);
    delete detector;
}

JNIEXPORT jobjectArray JNICALL
Java_com_example_detector_NativeDetector_detect(
    JNIEnv* env,
    jobject thiz,
    jlong detector_ptr,
    jobject bitmap
) {
    auto* detector = reinterpret_cast<detector::Detector*>(detector_ptr);
    
    auto detections = detector->detectFromBitmap(env, bitmap);
    
    // Convert to Java array
    jclass detection_class = env->FindClass("com/example/detector/Detection");
    jmethodID constructor = env->GetMethodID(detection_class, "<init>", "(IIIIFI)V");
    
    jobjectArray result = env->NewObjectArray(detections.size(), detection_class, nullptr);
    
    for (size_t i = 0; i < detections.size(); ++i) {
        const auto& det = detections[i];
        jobject obj = env->NewObject(
            detection_class, constructor,
            det.x, det.y, det.width, det.height,
            det.confidence, det.class_id
        );
        env->SetObjectArrayElement(result, i, obj);
    }
    
    return result;
}

}
```

**Kotlin wrapper:**

```kotlin
// NativeDetector.kt

package com.example.detector

import android.graphics.Bitmap

data class Detection(
    val x: Int,
    val y: Int,
    val width: Int,
    val height: Int,
    val confidence: Float,
    val classId: Int
)

class NativeDetector(
    modelPath: String,
    confThreshold: Float = 0.25f,
    iouThreshold: Float = 0.45f
) : AutoCloseable {
    
    private var nativePtr: Long = 0
    
    init {
        System.loadLibrary("detector")
        nativePtr = createDetector(modelPath, confThreshold, iouThreshold)
    }
    
    fun detect(bitmap: Bitmap): List<Detection> {
        require(nativePtr != 0L) { "Detector has been closed" }
        return detect(nativePtr, bitmap).toList()
    }
    
    override fun close() {
        if (nativePtr != 0L) {
            destroyDetector(nativePtr)
            nativePtr = 0
        }
    }
    
    private external fun createDetector(
        modelPath: String,
        confThreshold: Float,
        iouThreshold: Float
    ): Long
    
    private external fun destroyDetector(ptr: Long)
    
    private external fun detect(ptr: Long, bitmap: Bitmap): Array<Detection>
}
```

### 8.2.1. Android Use Case 1: SingleImageVerifier

```kotlin
// SingleImageVerifier.kt
// Use case: Quick test 1 image on device

package com.example.detector

import android.content.Context
import android.graphics.*
import android.net.Uri
import java.io.File
import java.io.FileOutputStream

/**
 * Verify detection on 1 image, output YOLO format.
 * 
 * Usage:
 *   val verifier = SingleImageVerifier(context, modelPath)
 *   val result = verifier.verify(imageUri)
 *   // result.outputImage: Bitmap với bboxes
 *   // result.yoloFile: File chứa results (YOLO format)
 */
class SingleImageVerifier(
    private val context: Context,
    modelPath: String,
    private val confThreshold: Float = 0.25f,
    private val iouThreshold: Float = 0.45f
) {
    private val detector = NativeDetector(modelPath, confThreshold, iouThreshold)
    private val labels: List<String> = loadLabels()
    
    data class VerifyResult(
        val detections: List<Detection>,
        val outputImage: Bitmap,
        val yoloFile: File,
        val inferenceTimeMs: Long
    )
    
    fun verify(imageUri: Uri, outputDir: File): VerifyResult {
        // Load image
        val inputStream = context.contentResolver.openInputStream(imageUri)
        val originalBitmap = BitmapFactory.decodeStream(inputStream)
        inputStream?.close()
        
        // Run detection
        val startTime = System.currentTimeMillis()
        val detections = detector.detect(originalBitmap)
        val inferenceTime = System.currentTimeMillis() - startTime
        
        // Draw bboxes
        val outputBitmap = drawDetections(originalBitmap, detections)
        
        // Save YOLO format
        val baseName = getBaseName(imageUri)
        val yoloFile = saveYoloFormat(
            detections, 
            originalBitmap.width, 
            originalBitmap.height,
            File(outputDir, "${baseName}.txt")
        )
        
        // Save output image
        val outputImageFile = File(outputDir, "${baseName}_result.jpg")
        FileOutputStream(outputImageFile).use { out ->
            outputBitmap.compress(Bitmap.CompressFormat.JPEG, 95, out)
        }
        
        return VerifyResult(detections, outputBitmap, yoloFile, inferenceTime)
    }
    
    private fun drawDetections(bitmap: Bitmap, detections: List<Detection>): Bitmap {
        val output = bitmap.copy(Bitmap.Config.ARGB_8888, true)
        val canvas = Canvas(output)
        val paint = Paint().apply {
            style = Paint.Style.STROKE
            strokeWidth = 3f
        }
        val textPaint = Paint().apply {
            color = Color.WHITE
            textSize = 32f
            typeface = Typeface.DEFAULT_BOLD
        }
        
        val colors = listOf(
            Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, 
            Color.CYAN, Color.MAGENTA, Color.rgb(255, 128, 0)
        )
        
        for (det in detections) {
            val color = colors[det.classId % colors.size]
            paint.color = color
            
            // Draw box
            canvas.drawRect(
                det.x.toFloat(), det.y.toFloat(),
                (det.x + det.width).toFloat(), (det.y + det.height).toFloat(),
                paint
            )
            
            // Draw label
            val label = "${labels.getOrElse(det.classId) { det.classId.toString() }} ${String.format("%.2f", det.confidence)}"
            val bgPaint = Paint().apply { color = color }
            canvas.drawRect(
                det.x.toFloat(), det.y.toFloat() - 40,
                det.x.toFloat() + textPaint.measureText(label) + 10, det.y.toFloat(),
                bgPaint
            )
            canvas.drawText(label, det.x.toFloat() + 5, det.y.toFloat() - 10, textPaint)
        }
        
        return output
    }
    
    private fun saveYoloFormat(
        detections: List<Detection>,
        imgWidth: Int,
        imgHeight: Int,
        outputFile: File
    ): File {
        outputFile.printWriter().use { out ->
            for (det in detections) {
                // Convert to YOLO format: class_id x_center y_center width height confidence
                val xCenter = (det.x + det.width / 2.0) / imgWidth
                val yCenter = (det.y + det.height / 2.0) / imgHeight
                val w = det.width.toDouble() / imgWidth
                val h = det.height.toDouble() / imgHeight
                out.println("${det.classId} ${"%.6f".format(xCenter)} ${"%.6f".format(yCenter)} ${"%.6f".format(w)} ${"%.6f".format(h)} ${"%.4f".format(det.confidence)}")
            }
        }
        return outputFile
    }
    
    private fun loadLabels(): List<String> {
        // Load from assets or return default
        return try {
            context.assets.open("labels.txt").bufferedReader().readLines()
        } catch (e: Exception) {
            emptyList()
        }
    }
    
    private fun getBaseName(uri: Uri): String {
        val path = uri.lastPathSegment ?: "image"
        return path.substringBeforeLast(".")
    }
    
    fun close() {
        detector.close()
    }
}
```

### 8.2.2. Android Use Case 2: BatchVerifier

```kotlin
// BatchVerifier.kt
// Use case: Batch evaluation, calculate mAP

package com.example.detector

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import java.io.File
import java.io.FileOutputStream

/**
 * Verify detection on image folder, output YOLO format for each image.
 * 
 * Usage:
 *   val verifier = BatchVerifier(context, modelPath)
 *   val results = verifier.verifyFolder(inputDir, outputDir) { progress ->
 *       // Update UI with progress (0.0 to 1.0)
 *   }
 */
class BatchVerifier(
    private val context: Context,
    modelPath: String,
    private val confThreshold: Float = 0.25f,
    private val iouThreshold: Float = 0.45f
) {
    private val detector = NativeDetector(modelPath, confThreshold, iouThreshold)
    private val labels: List<String> = loadLabels()
    
    data class BatchResult(
        val totalImages: Int,
        val processedImages: Int,
        val totalDetections: Int,
        val totalTimeMs: Long,
        val avgTimePerImageMs: Double,
        val outputDir: File
    )
    
    data class ImageResult(
        val imageName: String,
        val detections: Int,
        val timeMs: Long
    )
    
    fun verifyFolder(
        inputDir: File,
        outputDir: File,
        saveImages: Boolean = true,
        progressCallback: ((Float) -> Unit)? = null
    ): BatchResult {
        // Create output directories
        outputDir.mkdirs()
        val labelsDir = File(outputDir, "labels")
        labelsDir.mkdirs()
        val imagesDir = if (saveImages) File(outputDir, "images").apply { mkdirs() } else null
        
        // Find all images
        val imageExtensions = setOf("jpg", "jpeg", "png", "bmp")
        val imageFiles = inputDir.listFiles { file ->
            file.isFile && file.extension.lowercase() in imageExtensions
        }?.sortedBy { it.name } ?: emptyList()
        
        var totalDetections = 0
        var totalTime = 0L
        val results = mutableListOf<ImageResult>()
        
        for ((index, imageFile) in imageFiles.withIndex()) {
            val startTime = System.currentTimeMillis()
            
            // Load and detect
            val bitmap = BitmapFactory.decodeFile(imageFile.absolutePath)
            val detections = detector.detect(bitmap)
            
            val elapsed = System.currentTimeMillis() - startTime
            totalTime += elapsed
            totalDetections += detections.size
            
            // Save YOLO format
            val baseName = imageFile.nameWithoutExtension
            saveYoloFormat(
                detections,
                bitmap.width,
                bitmap.height,
                File(labelsDir, "$baseName.txt")
            )
            
            // Save image with bboxes (optional)
            if (saveImages && imagesDir != null) {
                val outputBitmap = drawDetections(bitmap, detections)
                FileOutputStream(File(imagesDir, "${baseName}_result.jpg")).use { out ->
                    outputBitmap.compress(Bitmap.CompressFormat.JPEG, 95, out)
                }
                outputBitmap.recycle()
            }
            
            bitmap.recycle()
            
            results.add(ImageResult(imageFile.name, detections.size, elapsed))
            progressCallback?.invoke((index + 1).toFloat() / imageFiles.size)
        }
        
        // Write summary
        writeSummary(results, outputDir)
        
        return BatchResult(
            totalImages = imageFiles.size,
            processedImages = results.size,
            totalDetections = totalDetections,
            totalTimeMs = totalTime,
            avgTimePerImageMs = if (results.isNotEmpty()) totalTime.toDouble() / results.size else 0.0,
            outputDir = outputDir
        )
    }
    
    private fun saveYoloFormat(
        detections: List<Detection>,
        imgWidth: Int,
        imgHeight: Int,
        outputFile: File
    ) {
        outputFile.printWriter().use { out ->
            for (det in detections) {
                val xCenter = (det.x + det.width / 2.0) / imgWidth
                val yCenter = (det.y + det.height / 2.0) / imgHeight
                val w = det.width.toDouble() / imgWidth
                val h = det.height.toDouble() / imgHeight
                out.println("${det.classId} ${"%.6f".format(xCenter)} ${"%.6f".format(yCenter)} ${"%.6f".format(w)} ${"%.6f".format(h)} ${"%.4f".format(det.confidence)}")
            }
        }
    }
    
    private fun drawDetections(bitmap: Bitmap, detections: List<Detection>): Bitmap {
        // Same as SingleImageVerifier.drawDetections()
        val output = bitmap.copy(Bitmap.Config.ARGB_8888, true)
        // ... (implementation same as SingleImageVerifier)
        return output
    }
    
    private fun writeSummary(results: List<ImageResult>, outputDir: File) {
        File(outputDir, "summary.txt").printWriter().use { out ->
            out.println("Batch Verification Summary")
            out.println("=" .repeat(50))
            out.println("Total images: ${results.size}")
            out.println("Total detections: ${results.sumOf { it.detections }}")
            out.println("Total time: ${results.sumOf { it.timeMs }} ms")
            out.println("Avg time/image: ${"%.2f".format(results.map { it.timeMs }.average())} ms")
            out.println()
            out.println("Per-image results:")
            out.println("-".repeat(50))
            for (r in results) {
                out.println("${r.imageName}: ${r.detections} detections, ${r.timeMs} ms")
            }
        }
    }
    
    private fun loadLabels(): List<String> {
        return try {
            context.assets.open("labels.txt").bufferedReader().readLines()
        } catch (e: Exception) {
            emptyList()
        }
    }
    
    fun close() {
        detector.close()
    }
}
```

### 8.2.3. Android Use Case 3: CameraFrameAnalyzer

```kotlin
// CameraFrameAnalyzer.kt
// Use case: Real-time detection từ camera

package com.example.detector

import android.graphics.Bitmap
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import java.util.concurrent.atomic.AtomicBoolean

/**
 * CameraX ImageAnalysis.Analyzer cho real-time detection.
 * 
 * Usage với CameraX:
 *   val analyzer = CameraFrameAnalyzer(modelPath) { detections ->
 *       // Update UI với detections
 *       runOnUiThread { overlayView.setDetections(detections) }
 *   }
 *   
 *   val imageAnalysis = ImageAnalysis.Builder()
 *       .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
 *       .build()
 *       .also { it.setAnalyzer(executor, analyzer) }
 */
class CameraFrameAnalyzer(
    modelPath: String,
    confThreshold: Float = 0.25f,
    iouThreshold: Float = 0.45f,
    private val onDetections: (List<Detection>, Int, Int, Long) -> Unit
) : ImageAnalysis.Analyzer {
    
    private val detector = NativeDetector(modelPath, confThreshold, iouThreshold)
    private val isProcessing = AtomicBoolean(false)
    
    override fun analyze(imageProxy: ImageProxy) {
        // Skip if still processing previous frame
        if (!isProcessing.compareAndSet(false, true)) {
            imageProxy.close()
            return
        }
        
        try {
            val startTime = System.currentTimeMillis()
            
            // Convert ImageProxy to Bitmap
            val bitmap = imageProxy.toBitmap()
            
            // Run detection
            val detections = detector.detect(bitmap)
            
            val inferenceTime = System.currentTimeMillis() - startTime
            
            // Callback with results
            onDetections(
                detections,
                imageProxy.width,
                imageProxy.height,
                inferenceTime
            )
            
            bitmap.recycle()
            
        } finally {
            isProcessing.set(false)
            imageProxy.close()
        }
    }
    
    /**
     * Convert ImageProxy to Bitmap.
     * Handles YUV_420_888 format from CameraX.
     */
    private fun ImageProxy.toBitmap(): Bitmap {
        val yBuffer = planes[0].buffer
        val uBuffer = planes[1].buffer
        val vBuffer = planes[2].buffer
        
        val ySize = yBuffer.remaining()
        val uSize = uBuffer.remaining()
        val vSize = vBuffer.remaining()
        
        val nv21 = ByteArray(ySize + uSize + vSize)
        
        yBuffer.get(nv21, 0, ySize)
        vBuffer.get(nv21, ySize, vSize)
        uBuffer.get(nv21, ySize + vSize, uSize)
        
        val yuvImage = android.graphics.YuvImage(
            nv21,
            android.graphics.ImageFormat.NV21,
            width,
            height,
            null
        )
        
        val out = java.io.ByteArrayOutputStream()
        yuvImage.compressToJpeg(android.graphics.Rect(0, 0, width, height), 90, out)
        val imageBytes = out.toByteArray()
        
        return android.graphics.BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size)
    }
    
    fun release() {
        detector.close()
    }
}

/**
 * Simple overlay view to draw detection results.
 * Extend View and override onDraw().
 */
// OverlayView.kt - separate file
/*
class DetectionOverlayView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {
    
    private var detections: List<Detection> = emptyList()
    private var sourceWidth: Int = 1
    private var sourceHeight: Int = 1
    
    private val boxPaint = Paint().apply {
        style = Paint.Style.STROKE
        strokeWidth = 4f
        color = Color.RED
    }
    
    private val textPaint = Paint().apply {
        color = Color.WHITE
        textSize = 40f
        typeface = Typeface.DEFAULT_BOLD
    }
    
    fun setDetections(detections: List<Detection>, srcWidth: Int, srcHeight: Int) {
        this.detections = detections
        this.sourceWidth = srcWidth
        this.sourceHeight = srcHeight
        invalidate()
    }
    
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        
        val scaleX = width.toFloat() / sourceWidth
        val scaleY = height.toFloat() / sourceHeight
        
        for (det in detections) {
            val left = det.x * scaleX
            val top = det.y * scaleY
            val right = (det.x + det.width) * scaleX
            val bottom = (det.y + det.height) * scaleY
            
            canvas.drawRect(left, top, right, bottom, boxPaint)
            canvas.drawText(
                "${det.classId}: ${String.format("%.2f", det.confidence)}",
                left, top - 10, textPaint
            )
        }
    }
}
*/
```

```kotlin
// FastPreprocessor.kt (Android)

package com.example.detector

import android.content.Context
import android.graphics.Bitmap
import android.renderscript.*

/**
 * GPU-accelerated preprocessing using RenderScript.
 * 
 * Performance: ~2-3ms for 640x640 (vs ~100ms CPU naive)
 * 
 * Note: RenderScript is deprecated in Android 12+. For newer apps,
 * consider using Vulkan Compute or OpenGL ES compute shaders.
 */
class FastPreprocessor(context: Context) {
    
    private val rs = RenderScript.create(context)
    private val scriptResize = ScriptIntrinsicResize.create(rs)
    private val scriptColorMatrix = ScriptIntrinsicColorMatrix.create(rs)
    
    private var inputAlloc: Allocation? = null
    private var resizedAlloc: Allocation? = null
    private var outputAlloc: Allocation? = null
    
    private val inputWidth = 640
    private val inputHeight = 640
    
    /**
     * Preprocess bitmap for model input.
     * 
     * @param bitmap Input bitmap (any size, ARGB_8888)
     * @return FloatArray in CHW format, normalized to [0,1]
     */
    fun preprocess(bitmap: Bitmap): FloatArray {
        // Lazy allocation
        if (inputAlloc == null || inputAlloc!!.type.x != bitmap.width) {
            inputAlloc?.destroy()
            inputAlloc = Allocation.createFromBitmap(
                rs, bitmap,
                Allocation.MipmapControl.MIPMAP_NONE,
                Allocation.USAGE_SCRIPT
            )
        } else {
            inputAlloc!!.copyFrom(bitmap)
        }
        
        // Resize allocation
        if (resizedAlloc == null) {
            val resizedType = Type.Builder(rs, Element.RGBA_8888(rs))
                .setX(inputWidth)
                .setY(inputHeight)
                .create()
            resizedAlloc = Allocation.createTyped(rs, resizedType, Allocation.USAGE_SCRIPT)
        }
        
        // Perform resize
        scriptResize.setInput(inputAlloc)
        scriptResize.forEach_bicubic(resizedAlloc)
        
        // Copy to byte array
        val pixels = ByteArray(inputWidth * inputHeight * 4)
        resizedAlloc!!.copyTo(pixels)
        
        // Convert to CHW float
        val tensor = FloatArray(3 * inputWidth * inputHeight)
        val planeSize = inputWidth * inputHeight
        
        for (i in 0 until planeSize) {
            val pixelOffset = i * 4
            // ARGB -> RGB, normalize to [0,1]
            tensor[i] = (pixels[pixelOffset + 1].toInt() and 0xFF) / 255f          // R
            tensor[planeSize + i] = (pixels[pixelOffset + 2].toInt() and 0xFF) / 255f  // G
            tensor[2 * planeSize + i] = (pixels[pixelOffset + 3].toInt() and 0xFF) / 255f // B
        }
        
        return tensor
    }
    
    fun release() {
        inputAlloc?.destroy()
        resizedAlloc?.destroy()
        outputAlloc?.destroy()
        scriptResize.destroy()
        scriptColorMatrix.destroy()
        rs.destroy()
    }
}
```

---

## 9. Generated C++ Code - iOS

This section contains C++/Objective-C++ and Swift code specifically for iOS platform.

### 9.1. iOS Use Cases and Output Files

```
┌─────────────────────────────────────────────────────────────────┐
│  iOS: 3 USE CASES                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  OPTION 1: Verify single image                                        │
│  ──────────────────────                                         │
│  Purpose: Quick test on device                              │
│  Output: image + bboxes, result.txt (YOLO format)                │
│                                                                 │
│  📁 output/                                                     │
│  ├── cpp/                                                       │
│  │   ├── detector_ios.hpp                                      │
│  │   ├── detector_ios.mm                                       │
│  │   └── CMakeLists.txt                                        │
│  ├── swift/                                                     │
│  │   ├── Detector.swift           # ObjC++ wrapper             │
│  │   └── SingleImageVerifier.swift # Verify single image             │
│  └── README.md                                                  │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  OPTION 2: Verify image folder                                  │
│  ────────────────────────────                                   │
│  Purpose: Batch evaluation, calculate mAP                          │
│  Output: images + bboxes, results/*.txt (YOLO format)             │
│                                                                 │
│  📁 output/                                                     │
│  ├── cpp/                                                       │
│  │   ├── detector_ios.hpp                                      │
│  │   ├── detector_ios.mm                                       │
│  │   └── CMakeLists.txt                                        │
│  ├── swift/                                                     │
│  │   ├── Detector.swift                                        │
│  │   └── BatchVerifier.swift      # Loop folder, save results │
│  └── README.md                                                  │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  OPTION 3: Camera integration (Production)                     │
│  ─────────────────────────────────────────                      │
│  Purpose: Real-time detection from camera                       │
│  Output: None - only return detections for app to handle           │
│                                                                 │
│  📁 output/                                                     │
│  ├── cpp/                                                       │
│  │   ├── detector_ios.hpp                                      │
│  │   ├── detector_ios.mm                                       │
│  │   └── CMakeLists.txt                                        │
│  ├── swift/                                                     │
│  │   ├── Detector.swift                                        │
│  │   └── CameraFrameProcessor.swift # AVCaptureSession        │
│  └── README.md                                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2. iOS Native Detector (CVPixelBuffer)

```cpp
// detector_ios.hpp

#pragma once
#include <onnxruntime_cxx_api.h>
#include <CoreVideo/CoreVideo.h>
#include <vector>
#include <memory>

namespace detector {

struct Detection {
    int x, y, width, height;
    float confidence;
    int class_id;
};

class Detector {
public:
    Detector(const std::string& model_path,
             float conf_threshold = 0.25f,
             float iou_threshold = 0.45f);
    
    /**
     * Detect from CVPixelBuffer (iOS camera/image).
     * 
     * Supported formats:
     * - kCVPixelFormatType_32BGRA
     * - kCVPixelFormatType_32RGBA
     * - kCVPixelFormatType_420YpCbCr8BiPlanarVideoRange (NV12)
     * - kCVPixelFormatType_420YpCbCr8BiPlanarFullRange
     */
    std::vector<Detection> detectFromPixelBuffer(CVPixelBufferRef pixelBuffer);

private:
    std::vector<float> preprocessPixelBuffer(CVPixelBufferRef pixelBuffer);
    std::vector<float> preprocessBGRA(const uint8_t* src, int width, int height, int stride);
    std::vector<float> preprocessNV12(CVPixelBufferRef pixelBuffer);
    
    std::vector<Detection> postprocess(
        const std::vector<float>& output,
        int orig_width, int orig_height
    );
    
    std::unique_ptr<Ort::Env> env_;
    std::unique_ptr<Ort::Session> session_;
    
    int input_width_ = {INPUT_WIDTH};
    int input_height_ = {INPUT_HEIGHT};
    float conf_threshold_;
    float iou_threshold_;
    float scale_;
    int pad_w_, pad_h_;
};

} // namespace detector
```

```cpp
// detector_ios.mm (Objective-C++)

#include "detector_ios.hpp"
#import <Accelerate/Accelerate.h>

namespace detector {

Detector::Detector(const std::string& model_path,
                   float conf_threshold,
                   float iou_threshold)
    : conf_threshold_(conf_threshold), iou_threshold_(iou_threshold) {
    
    env_ = std::make_unique<Ort::Env>(ORT_LOGGING_LEVEL_WARNING, "Detector");
    
    Ort::SessionOptions options;
    options.SetIntraOpNumThreads(4);
    
    // Enable CoreML for iOS acceleration
    // Ort::ThrowOnError(OrtSessionOptionsAppendExecutionProvider_CoreML(options, 0));
    
    session_ = std::make_unique<Ort::Session>(*env_, model_path.c_str(), options);
}

std::vector<Detection> Detector::detectFromPixelBuffer(CVPixelBufferRef pixelBuffer) {
    if (!pixelBuffer) return {};
    
    int width = static_cast<int>(CVPixelBufferGetWidth(pixelBuffer));
    int height = static_cast<int>(CVPixelBufferGetHeight(pixelBuffer));
    
    auto input_tensor = preprocessPixelBuffer(pixelBuffer);
    
    // Run inference...
    // ...
    
    return postprocess(output, width, height);
}

std::vector<float> Detector::preprocessPixelBuffer(CVPixelBufferRef pixelBuffer) {
    OSType format = CVPixelBufferGetPixelFormatType(pixelBuffer);
    
    CVPixelBufferLockBaseAddress(pixelBuffer, kCVPixelBufferLock_ReadOnly);
    
    std::vector<float> tensor;
    
    switch (format) {
        case kCVPixelFormatType_32BGRA:
        case kCVPixelFormatType_32RGBA: {
            uint8_t* baseAddress = static_cast<uint8_t*>(
                CVPixelBufferGetBaseAddress(pixelBuffer)
            );
            int width = static_cast<int>(CVPixelBufferGetWidth(pixelBuffer));
            int height = static_cast<int>(CVPixelBufferGetHeight(pixelBuffer));
            int stride = static_cast<int>(CVPixelBufferGetBytesPerRow(pixelBuffer));
            
            tensor = preprocessBGRA(baseAddress, width, height, stride);
            break;
        }
        
        case kCVPixelFormatType_420YpCbCr8BiPlanarVideoRange:
        case kCVPixelFormatType_420YpCbCr8BiPlanarFullRange: {
            tensor = preprocessNV12(pixelBuffer);
            break;
        }
        
        default:
            NSLog(@"Unsupported pixel format: %d", format);
            break;
    }
    
    CVPixelBufferUnlockBaseAddress(pixelBuffer, kCVPixelBufferLock_ReadOnly);
    
    return tensor;
}

std::vector<float> Detector::preprocessBGRA(
    const uint8_t* src,
    int width, int height, int stride
) {
    // Calculate letterbox
    scale_ = std::min(
        static_cast<float>(input_width_) / width,
        static_cast<float>(input_height_) / height
    );
    
    int new_w = static_cast<int>(width * scale_);
    int new_h = static_cast<int>(height * scale_);
    pad_w_ = (input_width_ - new_w) / 2;
    pad_h_ = (input_height_ - new_h) / 2;
    
    // Use Accelerate framework for fast resize
    vImage_Buffer srcBuffer = {
        .data = const_cast<uint8_t*>(src),
        .height = static_cast<vImagePixelCount>(height),
        .width = static_cast<vImagePixelCount>(width),
        .rowBytes = static_cast<size_t>(stride)
    };
    
    std::vector<uint8_t> resized(new_w * new_h * 4);
    vImage_Buffer dstBuffer = {
        .data = resized.data(),
        .height = static_cast<vImagePixelCount>(new_h),
        .width = static_cast<vImagePixelCount>(new_w),
        .rowBytes = static_cast<size_t>(new_w * 4)
    };
    
    vImageScale_ARGB8888(&srcBuffer, &dstBuffer, nullptr, kvImageNoFlags);
    
    // Convert to float tensor with padding
    std::vector<float> tensor(3 * input_height_ * input_width_, 114.0f / 255.0f);
    
    for (int y = 0; y < new_h; ++y) {
        for (int x = 0; x < new_w; ++x) {
            int src_idx = (y * new_w + x) * 4;
            
            // BGRA format
            uint8_t b = resized[src_idx + 0];
            uint8_t g = resized[src_idx + 1];
            uint8_t r = resized[src_idx + 2];
            
            int dst_y = y + pad_h_;
            int dst_x = x + pad_w_;
            
            // CHW format, RGB order
            tensor[0 * input_height_ * input_width_ + dst_y * input_width_ + dst_x] = r / 255.0f;
            tensor[1 * input_height_ * input_width_ + dst_y * input_width_ + dst_x] = g / 255.0f;
            tensor[2 * input_height_ * input_width_ + dst_y * input_width_ + dst_x] = b / 255.0f;
        }
    }
    
    return tensor;
}

std::vector<float> Detector::preprocessNV12(CVPixelBufferRef pixelBuffer) {
    // NV12 (YUV420) processing
    int width = static_cast<int>(CVPixelBufferGetWidth(pixelBuffer));
    int height = static_cast<int>(CVPixelBufferGetHeight(pixelBuffer));
    
    // Get Y and UV planes
    uint8_t* yPlane = static_cast<uint8_t*>(
        CVPixelBufferGetBaseAddressOfPlane(pixelBuffer, 0)
    );
    uint8_t* uvPlane = static_cast<uint8_t*>(
        CVPixelBufferGetBaseAddressOfPlane(pixelBuffer, 1)
    );
    
    int yStride = static_cast<int>(CVPixelBufferGetBytesPerRowOfPlane(pixelBuffer, 0));
    int uvStride = static_cast<int>(CVPixelBufferGetBytesPerRowOfPlane(pixelBuffer, 1));
    
    // Convert NV12 to RGB (simplified, consider using vImage for performance)
    std::vector<uint8_t> rgb(width * height * 3);
    
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            int yIdx = y * yStride + x;
            int uvIdx = (y / 2) * uvStride + (x / 2) * 2;
            
            int Y = yPlane[yIdx];
            int U = uvPlane[uvIdx] - 128;
            int V = uvPlane[uvIdx + 1] - 128;
            
            // YUV to RGB conversion
            int R = std::clamp(Y + 1.402 * V, 0.0, 255.0);
            int G = std::clamp(Y - 0.344 * U - 0.714 * V, 0.0, 255.0);
            int B = std::clamp(Y + 1.772 * U, 0.0, 255.0);
            
            int idx = (y * width + x) * 3;
            rgb[idx + 0] = static_cast<uint8_t>(R);
            rgb[idx + 1] = static_cast<uint8_t>(G);
            rgb[idx + 2] = static_cast<uint8_t>(B);
        }
    }
    
    // Now process RGB buffer (reuse BGRA logic with is_bgr=false)
    // ... (similar to preprocessBGRA but for RGB)
    
    return {};  // Placeholder
}

} // namespace detector
```

**Swift wrapper:**

```swift
// Detector.swift

import Foundation
import CoreVideo
import UIKit

class Detector {
    private var nativePtr: UnsafeMutableRawPointer?
    
    init(modelPath: String, confThreshold: Float = 0.25, iouThreshold: Float = 0.45) throws {
        nativePtr = detector_create(modelPath, confThreshold, iouThreshold)
        guard nativePtr != nil else {
            throw DetectorError.initializationFailed
        }
    }
    
    deinit {
        if let ptr = nativePtr {
            detector_destroy(ptr)
        }
    }
    
    func detect(pixelBuffer: CVPixelBuffer) -> [Detection] {
        guard let ptr = nativePtr else { return [] }
        
        var count: Int32 = 0
        guard let results = detector_detect(ptr, pixelBuffer, &count) else {
            return []
        }
        
        var detections: [Detection] = []
        for i in 0..<Int(count) {
            let det = results[i]
            detections.append(Detection(
                x: Int(det.x),
                y: Int(det.y),
                width: Int(det.width),
                height: Int(det.height),
                confidence: det.confidence,
                classId: Int(det.class_id)
            ))
        }
        
        detector_free_results(results)
        return detections
    }
    
    func detect(image: UIImage) -> [Detection] {
        guard let pixelBuffer = image.toPixelBuffer() else {
            return []
        }
        return detect(pixelBuffer: pixelBuffer)
    }
}

enum DetectorError: Error {
    case initializationFailed
}

struct Detection {
    let x: Int
    let y: Int
    let width: Int
    let height: Int
    let confidence: Float
    let classId: Int
}

extension UIImage {
    func toPixelBuffer() -> CVPixelBuffer? {
        let attrs = [
            kCVPixelBufferCGImageCompatibilityKey: kCFBooleanTrue,
            kCVPixelBufferCGBitmapContextCompatibilityKey: kCFBooleanTrue
        ] as CFDictionary
        
        var pixelBuffer: CVPixelBuffer?
        let status = CVPixelBufferCreate(
            kCFAllocatorDefault,
            Int(size.width),
            Int(size.height),
            kCVPixelFormatType_32BGRA,
            attrs,
            &pixelBuffer
        )
        
        guard status == kCVReturnSuccess, let buffer = pixelBuffer else {
            return nil
        }
        
        CVPixelBufferLockBaseAddress(buffer, [])
        defer { CVPixelBufferUnlockBaseAddress(buffer, []) }
        
        guard let context = CGContext(
            data: CVPixelBufferGetBaseAddress(buffer),
            width: Int(size.width),
            height: Int(size.height),
            bitsPerComponent: 8,
            bytesPerRow: CVPixelBufferGetBytesPerRow(buffer),
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue
        ) else {
            return nil
        }
        
        guard let cgImage = cgImage else { return nil }
        context.draw(cgImage, in: CGRect(origin: .zero, size: size))
        
        return buffer
    }
}
```

### 9.2.1. iOS Use Case 1: SingleImageVerifier

```swift
// SingleImageVerifier.swift
// Use case: Quick test 1 image on device

import Foundation
import UIKit

/// Verify detection on 1 image, output YOLO format.
///
/// Usage:
///   let verifier = try SingleImageVerifier(modelPath: modelPath)
///   let result = try verifier.verify(image: inputImage)
///   // result.outputImage: UIImage với bboxes
///   // result.yoloContent: String YOLO format
///
class SingleImageVerifier {
    private let detector: Detector
    private let labels: [String]
    
    struct VerifyResult {
        let detections: [Detection]
        let outputImage: UIImage
        let yoloContent: String
        let inferenceTimeMs: Double
    }
    
    init(modelPath: String, confThreshold: Float = 0.25, iouThreshold: Float = 0.45) throws {
        self.detector = try Detector(modelPath: modelPath, confThreshold: confThreshold, iouThreshold: iouThreshold)
        self.labels = SingleImageVerifier.loadLabels()
    }
    
    func verify(image: UIImage) throws -> VerifyResult {
        let startTime = CFAbsoluteTimeGetCurrent()
        
        // Run detection
        let detections = detector.detect(image: image)
        
        let inferenceTime = (CFAbsoluteTimeGetCurrent() - startTime) * 1000
        
        // Draw bboxes
        let outputImage = drawDetections(on: image, detections: detections)
        
        // Generate YOLO format
        let yoloContent = generateYoloFormat(
            detections: detections,
            imageWidth: Int(image.size.width),
            imageHeight: Int(image.size.height)
        )
        
        return VerifyResult(
            detections: detections,
            outputImage: outputImage,
            yoloContent: yoloContent,
            inferenceTimeMs: inferenceTime
        )
    }
    
    func verify(imageURL: URL, outputDir: URL) throws -> VerifyResult {
        guard let image = UIImage(contentsOfFile: imageURL.path) else {
            throw VerifierError.imageLoadFailed
        }
        
        let result = try verify(image: image)
        
        // Save output image
        let baseName = imageURL.deletingPathExtension().lastPathComponent
        let outputImageURL = outputDir.appendingPathComponent("\(baseName)_result.jpg")
        if let jpegData = result.outputImage.jpegData(compressionQuality: 0.95) {
            try jpegData.write(to: outputImageURL)
        }
        
        // Save YOLO format
        let yoloURL = outputDir.appendingPathComponent("\(baseName).txt")
        try result.yoloContent.write(to: yoloURL, atomically: true, encoding: .utf8)
        
        return result
    }
    
    private func drawDetections(on image: UIImage, detections: [Detection]) -> UIImage {
        UIGraphicsBeginImageContextWithOptions(image.size, false, image.scale)
        defer { UIGraphicsEndImageContext() }
        
        image.draw(at: .zero)
        
        guard let context = UIGraphicsGetCurrentContext() else {
            return image
        }
        
        let colors: [UIColor] = [.red, .green, .blue, .yellow, .cyan, .magenta, .orange]
        
        for det in detections {
            let color = colors[det.classId % colors.count]
            let rect = CGRect(x: det.x, y: det.y, width: det.width, height: det.height)
            
            // Draw box
            context.setStrokeColor(color.cgColor)
            context.setLineWidth(3)
            context.stroke(rect)
            
            // Draw label
            let label = "\(labels.indices.contains(det.classId) ? labels[det.classId] : "\(det.classId)") \(String(format: "%.2f", det.confidence))"
            let attrs: [NSAttributedString.Key: Any] = [
                .font: UIFont.boldSystemFont(ofSize: 16),
                .foregroundColor: UIColor.white,
                .backgroundColor: color
            ]
            let labelSize = label.size(withAttributes: attrs)
            let labelRect = CGRect(x: det.x, y: det.y - labelSize.height - 2, width: labelSize.width + 6, height: labelSize.height)
            
            context.setFillColor(color.cgColor)
            context.fill(labelRect)
            
            label.draw(at: CGPoint(x: det.x + 3, y: det.y - labelSize.height - 2), withAttributes: [
                .font: UIFont.boldSystemFont(ofSize: 16),
                .foregroundColor: UIColor.white
            ])
        }
        
        return UIGraphicsGetImageFromCurrentImageContext() ?? image
    }
    
    private func generateYoloFormat(detections: [Detection], imageWidth: Int, imageHeight: Int) -> String {
        var lines: [String] = []
        
        for det in detections {
            let xCenter = Double(det.x + det.width / 2) / Double(imageWidth)
            let yCenter = Double(det.y + det.height / 2) / Double(imageHeight)
            let w = Double(det.width) / Double(imageWidth)
            let h = Double(det.height) / Double(imageHeight)
            
            lines.append("\(det.classId) \(String(format: "%.6f", xCenter)) \(String(format: "%.6f", yCenter)) \(String(format: "%.6f", w)) \(String(format: "%.6f", h)) \(String(format: "%.4f", det.confidence))")
        }
        
        return lines.joined(separator: "\n")
    }
    
    private static func loadLabels() -> [String] {
        guard let path = Bundle.main.path(forResource: "labels", ofType: "txt"),
              let content = try? String(contentsOfFile: path) else {
            return []
        }
        return content.components(separatedBy: "\n").filter { !$0.isEmpty }
    }
}

enum VerifierError: Error {
    case imageLoadFailed
    case saveFailed
}
```

### 9.2.2. iOS Use Case 2: BatchVerifier

```swift
// BatchVerifier.swift
// Use case: Batch evaluation, calculate mAP

import Foundation
import UIKit

/// Verify detection on image folder, output YOLO format for each image.
///
/// Usage:
///   let verifier = try BatchVerifier(modelPath: modelPath)
///   let result = try verifier.verifyFolder(inputDir: inputURL, outputDir: outputURL) { progress in
///       print("Progress: \(progress * 100)%")
///   }
///
class BatchVerifier {
    private let detector: Detector
    private let labels: [String]
    
    struct BatchResult {
        let totalImages: Int
        let processedImages: Int
        let totalDetections: Int
        let totalTimeMs: Double
        let avgTimePerImageMs: Double
        let outputDir: URL
    }
    
    struct ImageResult {
        let imageName: String
        let detections: Int
        let timeMs: Double
    }
    
    init(modelPath: String, confThreshold: Float = 0.25, iouThreshold: Float = 0.45) throws {
        self.detector = try Detector(modelPath: modelPath, confThreshold: confThreshold, iouThreshold: iouThreshold)
        self.labels = BatchVerifier.loadLabels()
    }
    
    func verifyFolder(
        inputDir: URL,
        outputDir: URL,
        saveImages: Bool = true,
        progressCallback: ((Float) -> Void)? = nil
    ) throws -> BatchResult {
        // Create output directories
        let labelsDir = outputDir.appendingPathComponent("labels")
        try FileManager.default.createDirectory(at: labelsDir, withIntermediateDirectories: true)
        
        let imagesDir = saveImages ? outputDir.appendingPathComponent("images") : nil
        if let dir = imagesDir {
            try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        }
        
        // Find all images
        let imageExtensions = Set(["jpg", "jpeg", "png", "bmp"])
        let contents = try FileManager.default.contentsOfDirectory(at: inputDir, includingPropertiesForKeys: nil)
        let imageFiles = contents.filter { imageExtensions.contains($0.pathExtension.lowercased()) }.sorted { $0.lastPathComponent < $1.lastPathComponent }
        
        var totalDetections = 0
        var totalTime: Double = 0
        var results: [ImageResult] = []
        
        for (index, imageURL) in imageFiles.enumerated() {
            let startTime = CFAbsoluteTimeGetCurrent()
            
            // Load and detect
            guard let image = UIImage(contentsOfFile: imageURL.path) else { continue }
            let detections = detector.detect(image: image)
            
            let elapsed = (CFAbsoluteTimeGetCurrent() - startTime) * 1000
            totalTime += elapsed
            totalDetections += detections.count
            
            // Save YOLO format
            let baseName = imageURL.deletingPathExtension().lastPathComponent
            let yoloContent = generateYoloFormat(
                detections: detections,
                imageWidth: Int(image.size.width),
                imageHeight: Int(image.size.height)
            )
            try yoloContent.write(to: labelsDir.appendingPathComponent("\(baseName).txt"), atomically: true, encoding: .utf8)
            
            // Save image with bboxes (optional)
            if saveImages, let dir = imagesDir {
                let outputImage = drawDetections(on: image, detections: detections)
                if let jpegData = outputImage.jpegData(compressionQuality: 0.95) {
                    try jpegData.write(to: dir.appendingPathComponent("\(baseName)_result.jpg"))
                }
            }
            
            results.append(ImageResult(imageName: imageURL.lastPathComponent, detections: detections.count, timeMs: elapsed))
            progressCallback?(Float(index + 1) / Float(imageFiles.count))
        }
        
        // Write summary
        try writeSummary(results: results, outputDir: outputDir)
        
        return BatchResult(
            totalImages: imageFiles.count,
            processedImages: results.count,
            totalDetections: totalDetections,
            totalTimeMs: totalTime,
            avgTimePerImageMs: results.isEmpty ? 0 : totalTime / Double(results.count),
            outputDir: outputDir
        )
    }
    
    private func generateYoloFormat(detections: [Detection], imageWidth: Int, imageHeight: Int) -> String {
        var lines: [String] = []
        for det in detections {
            let xCenter = Double(det.x + det.width / 2) / Double(imageWidth)
            let yCenter = Double(det.y + det.height / 2) / Double(imageHeight)
            let w = Double(det.width) / Double(imageWidth)
            let h = Double(det.height) / Double(imageHeight)
            lines.append("\(det.classId) \(String(format: "%.6f", xCenter)) \(String(format: "%.6f", yCenter)) \(String(format: "%.6f", w)) \(String(format: "%.6f", h)) \(String(format: "%.4f", det.confidence))")
        }
        return lines.joined(separator: "\n")
    }
    
    private func drawDetections(on image: UIImage, detections: [Detection]) -> UIImage {
        // Same implementation as SingleImageVerifier
        UIGraphicsBeginImageContextWithOptions(image.size, false, image.scale)
        defer { UIGraphicsEndImageContext() }
        image.draw(at: .zero)
        // ... draw boxes and labels
        return UIGraphicsGetImageFromCurrentImageContext() ?? image
    }
    
    private func writeSummary(results: [ImageResult], outputDir: URL) throws {
        var content = "Batch Verification Summary\n"
        content += String(repeating: "=", count: 50) + "\n"
        content += "Total images: \(results.count)\n"
        content += "Total detections: \(results.reduce(0) { $0 + $1.detections })\n"
        content += "Total time: \(String(format: "%.1f", results.reduce(0) { $0 + $1.timeMs })) ms\n"
        content += "Avg time/image: \(String(format: "%.2f", results.map { $0.timeMs }.reduce(0, +) / Double(max(results.count, 1)))) ms\n\n"
        content += "Per-image results:\n"
        content += String(repeating: "-", count: 50) + "\n"
        for r in results {
            content += "\(r.imageName): \(r.detections) detections, \(String(format: "%.1f", r.timeMs)) ms\n"
        }
        
        try content.write(to: outputDir.appendingPathComponent("summary.txt"), atomically: true, encoding: .utf8)
    }
    
    private static func loadLabels() -> [String] {
        guard let path = Bundle.main.path(forResource: "labels", ofType: "txt"),
              let content = try? String(contentsOfFile: path) else {
            return []
        }
        return content.components(separatedBy: "\n").filter { !$0.isEmpty }
    }
}
```

### 9.2.3. iOS Use Case 3: CameraFrameProcessor

```swift
// CameraFrameProcessor.swift
// Use case: Real-time detection từ camera

import Foundation
import AVFoundation
import UIKit

/// AVCaptureVideoDataOutputSampleBufferDelegate cho real-time detection.
///
/// Usage:
///   let processor = try CameraFrameProcessor(modelPath: modelPath) { detections, size, timeMs in
///       DispatchQueue.main.async {
///           self.overlayView.setDetections(detections, sourceSize: size)
///       }
///   }
///   
///   // Setup AVCaptureSession
///   let videoOutput = AVCaptureVideoDataOutput()
///   videoOutput.setSampleBufferDelegate(processor, queue: processingQueue)
///
class CameraFrameProcessor: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    private let detector: Detector
    private let onDetections: ([Detection], CGSize, Double) -> Void
    private var isProcessing = false
    
    init(
        modelPath: String,
        confThreshold: Float = 0.25,
        iouThreshold: Float = 0.45,
        onDetections: @escaping ([Detection], CGSize, Double) -> Void
    ) throws {
        self.detector = try Detector(modelPath: modelPath, confThreshold: confThreshold, iouThreshold: iouThreshold)
        self.onDetections = onDetections
        super.init()
    }
    
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        // Skip if still processing
        guard !isProcessing else { return }
        isProcessing = true
        
        defer { isProcessing = false }
        
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        
        let startTime = CFAbsoluteTimeGetCurrent()
        
        // Run detection
        let detections = detector.detect(pixelBuffer: pixelBuffer)
        
        let inferenceTime = (CFAbsoluteTimeGetCurrent() - startTime) * 1000
        
        // Get frame size
        let width = CVPixelBufferGetWidth(pixelBuffer)
        let height = CVPixelBufferGetHeight(pixelBuffer)
        let size = CGSize(width: width, height: height)
        
        // Callback with results
        onDetections(detections, size, inferenceTime)
    }
}

/// Simple overlay view to draw detection results on camera preview.
class DetectionOverlayView: UIView {
    private var detections: [Detection] = []
    private var sourceSize: CGSize = .zero
    private let labels: [String]
    
    private let colors: [UIColor] = [.red, .green, .blue, .yellow, .cyan, .magenta, .orange]
    
    override init(frame: CGRect) {
        self.labels = DetectionOverlayView.loadLabels()
        super.init(frame: frame)
        backgroundColor = .clear
    }
    
    required init?(coder: NSCoder) {
        self.labels = DetectionOverlayView.loadLabels()
        super.init(coder: coder)
        backgroundColor = .clear
    }
    
    func setDetections(_ detections: [Detection], sourceSize: CGSize) {
        self.detections = detections
        self.sourceSize = sourceSize
        setNeedsDisplay()
    }
    
    override func draw(_ rect: CGRect) {
        super.draw(rect)
        
        guard let context = UIGraphicsGetCurrentContext(), sourceSize.width > 0 else { return }
        
        let scaleX = bounds.width / sourceSize.width
        let scaleY = bounds.height / sourceSize.height
        
        for det in detections {
            let color = colors[det.classId % colors.count]
            
            let boxRect = CGRect(
                x: CGFloat(det.x) * scaleX,
                y: CGFloat(det.y) * scaleY,
                width: CGFloat(det.width) * scaleX,
                height: CGFloat(det.height) * scaleY
            )
            
            // Draw box
            context.setStrokeColor(color.cgColor)
            context.setLineWidth(3)
            context.stroke(boxRect)
            
            // Draw label
            let label = "\(labels.indices.contains(det.classId) ? labels[det.classId] : "\(det.classId)"): \(String(format: "%.2f", det.confidence))"
            let attrs: [NSAttributedString.Key: Any] = [
                .font: UIFont.boldSystemFont(ofSize: 14),
                .foregroundColor: UIColor.white
            ]
            let labelSize = label.size(withAttributes: attrs)
            
            // Background for label
            context.setFillColor(color.cgColor)
            context.fill(CGRect(x: boxRect.minX, y: boxRect.minY - labelSize.height - 4, width: labelSize.width + 8, height: labelSize.height + 4))
            
            label.draw(at: CGPoint(x: boxRect.minX + 4, y: boxRect.minY - labelSize.height - 2), withAttributes: attrs)
        }
    }
    
    private static func loadLabels() -> [String] {
        guard let path = Bundle.main.path(forResource: "labels", ofType: "txt"),
              let content = try? String(contentsOfFile: path) else {
            return []
        }
        return content.components(separatedBy: "\n").filter { !$0.isEmpty }
    }
}

/// Example usage with AVCaptureSession
///
/// class CameraViewController: UIViewController {
///     private var captureSession: AVCaptureSession!
///     private var previewLayer: AVCaptureVideoPreviewLayer!
///     private var overlayView: DetectionOverlayView!
///     private var processor: CameraFrameProcessor!
///     private let processingQueue = DispatchQueue(label: "detection.processing")
///     
///     override func viewDidLoad() {
///         super.viewDidLoad()
///         setupCamera()
///     }
///     
///     private func setupCamera() {
///         captureSession = AVCaptureSession()
///         captureSession.sessionPreset = .hd1280x720
///         
///         guard let camera = AVCaptureDevice.default(for: .video),
///               let input = try? AVCaptureDeviceInput(device: camera) else { return }
///         
///         captureSession.addInput(input)
///         
///         // Preview layer
///         previewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
///         previewLayer.frame = view.bounds
///         previewLayer.videoGravity = .resizeAspectFill
///         view.layer.addSublayer(previewLayer)
///         
///         // Overlay view
///         overlayView = DetectionOverlayView(frame: view.bounds)
///         view.addSubview(overlayView)
///         
///         // Video output for processing
///         let videoOutput = AVCaptureVideoDataOutput()
///         videoOutput.setSampleBufferDelegate(processor, queue: processingQueue)
///         captureSession.addOutput(videoOutput)
///         
///         // Setup processor
///         let modelPath = Bundle.main.path(forResource: "model", ofType: "onnx")!
///         processor = try! CameraFrameProcessor(modelPath: modelPath) { [weak self] detections, size, timeMs in
///             DispatchQueue.main.async {
///                 self?.overlayView.setDetections(detections, sourceSize: size)
///             }
///         }
///         
///         captureSession.startRunning()
///     }
/// }
```

```swift
// MetalPreprocessor.swift

import Metal
import MetalPerformanceShaders
import CoreVideo

/**
 * GPU-accelerated preprocessing using Metal.
 * 
 * Performance: ~1-2ms cho 640x640
 * 
 * Pipeline:
 * 1. CVPixelBuffer -> MTLTexture (zero-copy when possible)
 * 2. MPSImageBilinearScale for resize
 * 3. Custom kernel for HWC->CHW + normalize
 */
class MetalPreprocessor {
    
    private let device: MTLDevice
    private let commandQueue: MTLCommandQueue
    private let scaler: MPSImageBilinearScale
    private let textureCache: CVMetalTextureCache
    
    private let inputWidth = 640
    private let inputHeight = 640
    
    // Reusable textures
    private var resizedTexture: MTLTexture?
    
    init?() {
        guard let device = MTLCreateSystemDefaultDevice(),
              let commandQueue = device.makeCommandQueue() else {
            return nil
        }
        
        self.device = device
        self.commandQueue = commandQueue
        self.scaler = MPSImageBilinearScale(device: device)
        
        // Create texture cache for CVPixelBuffer -> MTLTexture
        var cache: CVMetalTextureCache?
        CVMetalTextureCacheCreate(nil, nil, device, nil, &cache)
        guard let textureCache = cache else { return nil }
        self.textureCache = textureCache
        
        // Pre-allocate resized texture
        let desc = MTLTextureDescriptor.texture2DDescriptor(
            pixelFormat: .rgba8Unorm,
            width: inputWidth,
            height: inputHeight,
            mipmapped: false
        )
        desc.usage = [.shaderRead, .shaderWrite]
        self.resizedTexture = device.makeTexture(descriptor: desc)
    }
    
    /**
     * Preprocess CVPixelBuffer from camera/image.
     */
    func preprocess(_ pixelBuffer: CVPixelBuffer) -> [Float]? {
        // Convert CVPixelBuffer to MTLTexture
        guard let inputTexture = createTexture(from: pixelBuffer),
              let resizedTexture = resizedTexture,
              let commandBuffer = commandQueue.makeCommandBuffer() else {
            return nil
        }
        
        // Resize
        scaler.encode(commandBuffer: commandBuffer,
                      sourceTexture: inputTexture,
                      destinationTexture: resizedTexture)
        
        commandBuffer.commit()
        commandBuffer.waitUntilCompleted()
        
        // Read back and convert to CHW
        return textureToTensor(resizedTexture)
    }
    
    private func createTexture(from pixelBuffer: CVPixelBuffer) -> MTLTexture? {
        let width = CVPixelBufferGetWidth(pixelBuffer)
        let height = CVPixelBufferGetHeight(pixelBuffer)
        
        var cvTexture: CVMetalTexture?
        let status = CVMetalTextureCacheCreateTextureFromImage(
            nil,
            textureCache,
            pixelBuffer,
            nil,
            .bgra8Unorm,
            width,
            height,
            0,
            &cvTexture
        )
        
        guard status == kCVReturnSuccess, let cvTexture = cvTexture else {
            return nil
        }
        
        return CVMetalTextureGetTexture(cvTexture)
    }
    
    private func textureToTensor(_ texture: MTLTexture) -> [Float] {
        let width = texture.width
        let height = texture.height
        let planeSize = width * height
        
        // Read pixels
        var pixels = [UInt8](repeating: 0, count: width * height * 4)
        texture.getBytes(
            &pixels,
            bytesPerRow: width * 4,
            from: MTLRegionMake2D(0, 0, width, height),
            mipmapLevel: 0
        )
        
        // Convert BGRA -> RGB CHW, normalize
        var tensor = [Float](repeating: 0, count: 3 * planeSize)
        
        for i in 0..<planeSize {
            let pixelOffset = i * 4
            let b = Float(pixels[pixelOffset]) / 255.0
            let g = Float(pixels[pixelOffset + 1]) / 255.0
            let r = Float(pixels[pixelOffset + 2]) / 255.0
            
            tensor[i] = r                    // R plane
            tensor[planeSize + i] = g        // G plane
            tensor[2 * planeSize + i] = b    // B plane
        }
        
        return tensor
    }
}
```

---

## 10. Optimized Preprocessing (Cross-Platform)

Going back to Core code, these are common optimizations for all platforms.

### 10.1. stb_image Mode (Lightweight)

```cpp
// detector_stb.hpp

#pragma once

// Single header, include in ONE .cpp file with this define:
// #define STB_IMAGE_IMPLEMENTATION
// #include "stb_image.h"

#include <onnxruntime_cxx_api.h>
#include <vector>
#include <string>
#include <memory>

namespace detector {

struct Detection {
    int x, y, width, height;
    float confidence;
    int class_id;
};

/**
 * Lightweight detector using stb_image for image loading.
 * 
 * Dependencies: Only stb_image.h (single header)
 * Limitations: No advanced image processing (use for simple file loading)
 */
class Detector {
public:
    Detector(const std::string& model_path,
             float conf_threshold = 0.25f,
             float iou_threshold = 0.45f);
    
    /**
     * Detect from image file.
     * Supported formats: JPEG, PNG, BMP, GIF, PSD, TGA, HDR, PIC
     */
    std::vector<Detection> detectFromFile(const std::string& image_path);
    
    /**
     * Detect from memory buffer containing image file data.
     */
    std::vector<Detection> detectFromMemory(
        const unsigned char* buffer,
        int buffer_size
    );
    
    /**
     * Detect from raw RGB pixels.
     */
    std::vector<Detection> detectFromPixels(
        const unsigned char* pixels,
        int width, int height,
        int channels = 3
    );

private:
    std::vector<float> preprocess(
        const unsigned char* pixels,
        int width, int height,
        int channels
    );
    
    void resize_nearest(
        const unsigned char* src, int src_w, int src_h,
        unsigned char* dst, int dst_w, int dst_h,
        int channels
    );
    
    std::vector<Detection> postprocess(
        const std::vector<float>& output,
        int orig_width, int orig_height
    );
    
    std::unique_ptr<Ort::Env> env_;
    std::unique_ptr<Ort::Session> session_;
    
    int input_width_ = {INPUT_WIDTH};
    int input_height_ = {INPUT_HEIGHT};
    float conf_threshold_;
    float iou_threshold_;
    float scale_;
    int pad_w_, pad_h_;
};

} // namespace detector
```

```cpp
// detector_stb.cpp

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

#include "detector_stb.hpp"
#include <algorithm>
#include <cstring>
#include <stdexcept>

namespace detector {

Detector::Detector(const std::string& model_path,
                   float conf_threshold,
                   float iou_threshold)
    : conf_threshold_(conf_threshold), iou_threshold_(iou_threshold) {
    
    env_ = std::make_unique<Ort::Env>(ORT_LOGGING_LEVEL_WARNING, "Detector");
    Ort::SessionOptions options;
    options.SetIntraOpNumThreads(4);
    session_ = std::make_unique<Ort::Session>(*env_, model_path.c_str(), options);
}

std::vector<Detection> Detector::detectFromFile(const std::string& image_path) {
    int width, height, channels;
    
    // Load image using stb_image (always request 3 channels = RGB)
    unsigned char* pixels = stbi_load(
        image_path.c_str(),
        &width, &height, &channels,
        3  // Force RGB output
    );
    
    if (!pixels) {
        throw std::runtime_error("Failed to load image: " + image_path +
                                 " - " + stbi_failure_reason());
    }
    
    auto detections = detectFromPixels(pixels, width, height, 3);
    
    stbi_image_free(pixels);
    
    return detections;
}

std::vector<Detection> Detector::detectFromMemory(
    const unsigned char* buffer,
    int buffer_size
) {
    int width, height, channels;
    
    unsigned char* pixels = stbi_load_from_memory(
        buffer, buffer_size,
        &width, &height, &channels,
        3  // Force RGB
    );
    
    if (!pixels) {
        throw std::runtime_error(std::string("Failed to load image from memory: ") +
                                 stbi_failure_reason());
    }
    
    auto detections = detectFromPixels(pixels, width, height, 3);
    
    stbi_image_free(pixels);
    
    return detections;
}

std::vector<Detection> Detector::detectFromPixels(
    const unsigned char* pixels,
    int width, int height,
    int channels
) {
    if (!pixels || width <= 0 || height <= 0) {
        return {};
    }
    
    auto input_tensor = preprocess(pixels, width, height, channels);
    
    // Run ONNX inference
    // ...
    
    return postprocess(output, width, height);
}

void Detector::resize_nearest(
    const unsigned char* src, int src_w, int src_h,
    unsigned char* dst, int dst_w, int dst_h,
    int channels
) {
    float x_ratio = static_cast<float>(src_w) / dst_w;
    float y_ratio = static_cast<float>(src_h) / dst_h;
    
    for (int y = 0; y < dst_h; ++y) {
        for (int x = 0; x < dst_w; ++x) {
            int src_x = static_cast<int>(x * x_ratio);
            int src_y = static_cast<int>(y * y_ratio);
            
            for (int c = 0; c < channels; ++c) {
                dst[(y * dst_w + x) * channels + c] =
                    src[(src_y * src_w + src_x) * channels + c];
            }
        }
    }
}

std::vector<float> Detector::preprocess(
    const unsigned char* pixels,
    int width, int height,
    int channels
) {
    // Calculate letterbox parameters
    scale_ = std::min(
        static_cast<float>(input_width_) / width,
        static_cast<float>(input_height_) / height
    );
    
    int new_w = static_cast<int>(width * scale_);
    int new_h = static_cast<int>(height * scale_);
    pad_w_ = (input_width_ - new_w) / 2;
    pad_h_ = (input_height_ - new_h) / 2;
    
    // Resize
    std::vector<unsigned char> resized(new_w * new_h * channels);
    resize_nearest(pixels, width, height,
                   resized.data(), new_w, new_h, channels);
    
    // Create padded tensor with gray padding
    std::vector<float> tensor(3 * input_height_ * input_width_, 114.0f / 255.0f);
    
    // Copy resized pixels with normalization
    for (int y = 0; y < new_h; ++y) {
        for (int x = 0; x < new_w; ++x) {
            int src_idx = (y * new_w + x) * channels;
            int dst_y = y + pad_h_;
            int dst_x = x + pad_w_;
            
            // stb_image outputs RGB when we request 3 channels
            // CHW format
            tensor[0 * input_height_ * input_width_ + dst_y * input_width_ + dst_x] =
                resized[src_idx + 0] / 255.0f;  // R
            tensor[1 * input_height_ * input_width_ + dst_y * input_width_ + dst_x] =
                resized[src_idx + 1] / 255.0f;  // G
            tensor[2 * input_height_ * input_width_ + dst_y * input_width_ + dst_x] =
                resized[src_idx + 2] / 255.0f;  // B
        }
    }
    
    return tensor;
}

} // namespace detector
```

### 10.2. Performance Issues on Mobile

```
┌─────────────────────────────────────────────────────────────────┐
│                    PREPROCESSING BOTTLENECK                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Naive implementation cho 640x640 RGB image:                   │
│                                                                 │
│  • 640 × 640 × 3 = 1,228,800 pixel operations                  │
│  • Mỗi pixel: load + convert + normalize + store               │
│  • Time: 100-200ms on mobile CPU                        │
│                                                                 │
│  Main issues:                                                 │
│  • Frequent cache misses (non-contiguous access)               │
│  • Not utilizing SIMD (NEON on ARM)                         │
│  • Malloc/free mỗi frame                                       │
│  • Division instead of multiplication                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 10.3. Performance Comparison of Methods

| Method | Time (640×640) | Speedup | Notes |
|--------|----------------|---------|---------|
| Naive loop | ~150ms | 1× | Baseline |
| Row-wise copy | ~80ms | 2× | Better cache |
| NEON basic | ~25ms | 6× | SIMD 4-8 pixels |
| NEON + vld3 | ~10ms | 15× | Deinterleave hardware |
| vImage/Accelerate | ~5-8ms | 20× | iOS optimized |
| GPU preprocessing | ~2-3ms | 50× | Best, but complex |

### 10.4. Optimized Preprocessing Implementation

```cpp
// optimized_preprocess.hpp

#pragma once
#include <cstdint>
#include <vector>
#include <memory>

#if defined(__ARM_NEON) || defined(__ARM_NEON__)
#include <arm_neon.h>
#define USE_NEON 1
#else
#define USE_NEON 0
#endif

#if defined(__APPLE__)
#include <Accelerate/Accelerate.h>
#define USE_ACCELERATE 1
#else
#define USE_ACCELERATE 0
#endif

namespace detector {

/**
 * Optimized preprocessing với:
 * - Buffer reuse (no malloc per frame)
 * - SIMD (NEON on ARM)
 * - Platform-specific acceleration (vImage, etc.)
 * - Cache-friendly memory access
 */
class OptimizedPreprocessor {
public:
    OptimizedPreprocessor(int input_width, int input_height);
    ~OptimizedPreprocessor() = default;
    
    // Non-copyable, movable
    OptimizedPreprocessor(const OptimizedPreprocessor&) = delete;
    OptimizedPreprocessor& operator=(const OptimizedPreprocessor&) = delete;
    OptimizedPreprocessor(OptimizedPreprocessor&&) = default;
    OptimizedPreprocessor& operator=(OptimizedPreprocessor&&) = default;
    
    /**
     * Preprocess image with maximum optimization.
     * 
     * @param src_pixels    Source pixels (HWC format, uint8_t, RGB hoặc BGR)
     * @param src_width     Source width
     * @param src_height    Source height
     * @param src_channels  Number of channels (3 hoặc 4)
     * @param is_bgr        True nếu BGR, false nếu RGB
     * @return              Pointer to internal buffer (CHW format, float, normalized)
     * 
     * NOTE: Returned pointer valid until next preprocess() call
     */
    const float* preprocess(
        const uint8_t* src_pixels,
        int src_width,
        int src_height,
        int src_channels = 3,
        bool is_bgr = false
    );
    
    // Getters for letterbox info (to convert coordinates later)
    float getScale() const { return scale_; }
    int getPadX() const { return pad_x_; }
    int getPadY() const { return pad_y_; }
    
    // Tensor size
    size_t getTensorSize() const { return tensor_buffer_.size(); }
    
private:
    // Target dimensions
    int input_width_;
    int input_height_;
    
    // Letterbox info
    float scale_ = 1.0f;
    int pad_x_ = 0;
    int pad_y_ = 0;
    
    // Pre-allocated buffers (IMPORTANT: no malloc per frame)
    std::vector<uint8_t> resize_buffer_;    // Buffer cho resized image
    std::vector<float> tensor_buffer_;       // Output tensor (CHW format)
    
    // Preprocessing steps
    void resize_fast(
        const uint8_t* src, int src_w, int src_h, int channels,
        uint8_t* dst, int dst_w, int dst_h
    );
    
    void hwc_to_chw_normalized(
        const uint8_t* src,
        int width, int height,
        int channels, bool is_bgr
    );
    
    // NEON optimized functions
#if USE_NEON
    void hwc_to_chw_neon(const uint8_t* src, int width, int height, bool is_bgr);
    void normalize_neon(const uint8_t* src, float* dst, int count);
#endif
    
    // Accelerate framework (iOS)
#if USE_ACCELERATE
    void resize_vimage(
        const uint8_t* src, int src_w, int src_h,
        uint8_t* dst, int dst_w, int dst_h,
        int channels
    );
#endif
};

} // namespace detector
```

```cpp
// optimized_preprocess.cpp

#include "optimized_preprocess.hpp"
#include <algorithm>
#include <cstring>
#include <cmath>

namespace detector {

OptimizedPreprocessor::OptimizedPreprocessor(int input_width, int input_height)
    : input_width_(input_width)
    , input_height_(input_height)
{
    // Pre-allocate buffers (CHỈ MALLOC MỘT LẦN)
    resize_buffer_.resize(input_width * input_height * 4);  // Max 4 channels
    tensor_buffer_.resize(3 * input_width * input_height);
    
    // Fill tensor with padding value (114/255 ≈ 0.447)
    std::fill(tensor_buffer_.begin(), tensor_buffer_.end(), 114.0f / 255.0f);
}

const float* OptimizedPreprocessor::preprocess(
    const uint8_t* src_pixels,
    int src_width,
    int src_height,
    int src_channels,
    bool is_bgr
) {
    // ─────────────────────────────────────────────────────────────
    // Step 1: Calculate letterbox parameters
    // ─────────────────────────────────────────────────────────────
    scale_ = std::min(
        static_cast<float>(input_width_) / src_width,
        static_cast<float>(input_height_) / src_height
    );
    
    int new_w = static_cast<int>(src_width * scale_);
    int new_h = static_cast<int>(src_height * scale_);
    
    pad_x_ = (input_width_ - new_w) / 2;
    pad_y_ = (input_height_ - new_h) / 2;
    
    // ─────────────────────────────────────────────────────────────
    // Step 2: Resize
    // ─────────────────────────────────────────────────────────────
#if USE_ACCELERATE
    resize_vimage(src_pixels, src_width, src_height,
                  resize_buffer_.data(), new_w, new_h, src_channels);
#else
    resize_fast(src_pixels, src_width, src_height, src_channels,
                resize_buffer_.data(), new_w, new_h);
#endif
    
    // ─────────────────────────────────────────────────────────────
    // Step 3: Reset padding areas (only when needed)
    // ─────────────────────────────────────────────────────────────
    // Optimization: only reset if letterbox changes
    // In practice, if input size is fixed, can skip this step
    
    // ─────────────────────────────────────────────────────────────
    // Step 4: HWC to CHW + Normalize
    // ─────────────────────────────────────────────────────────────
#if USE_NEON
    hwc_to_chw_neon(resize_buffer_.data(), new_w, new_h, is_bgr);
#else
    hwc_to_chw_normalized(resize_buffer_.data(), new_w, new_h, src_channels, is_bgr);
#endif
    
    return tensor_buffer_.data();
}

// ─────────────────────────────────────────────────────────────────
// Fast Resize (Bilinear, cache-friendly)
// ─────────────────────────────────────────────────────────────────

void OptimizedPreprocessor::resize_fast(
    const uint8_t* src, int src_w, int src_h, int channels,
    uint8_t* dst, int dst_w, int dst_h
) {
    const float x_ratio = static_cast<float>(src_w) / dst_w;
    const float y_ratio = static_cast<float>(src_h) / dst_h;
    
    // Process row by row (cache friendly)
    for (int y = 0; y < dst_h; ++y) {
        const float src_y = y * y_ratio;
        const int y0 = static_cast<int>(src_y);
        const int y1 = std::min(y0 + 1, src_h - 1);
        const float y_diff = src_y - y0;
        const float y_diff_inv = 1.0f - y_diff;
        
        // Pre-calculate row pointers
        const uint8_t* row0 = src + y0 * src_w * channels;
        const uint8_t* row1 = src + y1 * src_w * channels;
        uint8_t* dst_row = dst + y * dst_w * channels;
        
        for (int x = 0; x < dst_w; ++x) {
            const float src_x = x * x_ratio;
            const int x0 = static_cast<int>(src_x);
            const int x1 = std::min(x0 + 1, src_w - 1);
            const float x_diff = src_x - x0;
            const float x_diff_inv = 1.0f - x_diff;
            
            // Bilinear interpolation weights
            const float w00 = x_diff_inv * y_diff_inv;
            const float w01 = x_diff * y_diff_inv;
            const float w10 = x_diff_inv * y_diff;
            const float w11 = x_diff * y_diff;
            
            // Process all channels
            for (int c = 0; c < channels; ++c) {
                float val = 
                    row0[x0 * channels + c] * w00 +
                    row0[x1 * channels + c] * w01 +
                    row1[x0 * channels + c] * w10 +
                    row1[x1 * channels + c] * w11;
                
                dst_row[x * channels + c] = static_cast<uint8_t>(val);
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────
// HWC to CHW + Normalize (Scalar fallback)
// ─────────────────────────────────────────────────────────────────

void OptimizedPreprocessor::hwc_to_chw_normalized(
    const uint8_t* src,
    int width, int height,
    int channels, bool is_bgr
) {
    const int plane_size = input_width_ * input_height_;
    const float scale = 1.0f / 255.0f;  // Multiplication instead of division
    
    float* dst_r = tensor_buffer_.data();
    float* dst_g = tensor_buffer_.data() + plane_size;
    float* dst_b = tensor_buffer_.data() + plane_size * 2;
    
    const int r_idx = is_bgr ? 2 : 0;
    const int b_idx = is_bgr ? 0 : 2;
    
    // Process với padding offset
    for (int y = 0; y < height; ++y) {
        const int dst_y = y + pad_y_;
        const uint8_t* src_row = src + y * width * channels;
        
        for (int x = 0; x < width; ++x) {
            const int dst_x = x + pad_x_;
            const int dst_idx = dst_y * input_width_ + dst_x;
            const int src_idx = x * channels;
            
            dst_r[dst_idx] = src_row[src_idx + r_idx] * scale;
            dst_g[dst_idx] = src_row[src_idx + 1] * scale;
            dst_b[dst_idx] = src_row[src_idx + b_idx] * scale;
        }
    }
}

// ─────────────────────────────────────────────────────────────────
// NEON Optimized Implementation
// ─────────────────────────────────────────────────────────────────

#if USE_NEON

void OptimizedPreprocessor::hwc_to_chw_neon(
    const uint8_t* src,
    int width, int height,
    bool is_bgr
) {
    const int plane_size = input_width_ * input_height_;
    const float32x4_t scale = vdupq_n_f32(1.0f / 255.0f);
    
    float* dst_r = tensor_buffer_.data();
    float* dst_g = tensor_buffer_.data() + plane_size;
    float* dst_b = tensor_buffer_.data() + plane_size * 2;
    
    for (int y = 0; y < height; ++y) {
        const int dst_y = y + pad_y_;
        const uint8_t* src_row = src + y * width * 3;
        
        int x = 0;
        
        // Process 8 pixels at a time với NEON
        for (; x + 8 <= width; x += 8) {
            const int dst_x = x + pad_x_;
            const int dst_idx = dst_y * input_width_ + dst_x;
            
            // vld3_u8: Load 24 bytes and deinterleave into 3 vectors of 8 bytes
            // This is key optimization - hardware auto deinterleaves!
            uint8x8x3_t rgb = vld3_u8(src_row + x * 3);
            
            // Select channel based on BGR/RGB
            uint8x8_t r_u8 = is_bgr ? rgb.val[2] : rgb.val[0];
            uint8x8_t g_u8 = rgb.val[1];
            uint8x8_t b_u8 = is_bgr ? rgb.val[0] : rgb.val[2];
            
            // ─────────────────────────────────────────────────────
            // Process R channel: uint8 → uint16 → uint32 → float
            // ─────────────────────────────────────────────────────
            uint16x8_t r_u16 = vmovl_u8(r_u8);
            
            // Low 4 pixels
            uint32x4_t r_lo_u32 = vmovl_u16(vget_low_u16(r_u16));
            float32x4_t r_lo_f32 = vmulq_f32(vcvtq_f32_u32(r_lo_u32), scale);
            vst1q_f32(dst_r + dst_idx, r_lo_f32);
            
            // High 4 pixels
            uint32x4_t r_hi_u32 = vmovl_u16(vget_high_u16(r_u16));
            float32x4_t r_hi_f32 = vmulq_f32(vcvtq_f32_u32(r_hi_u32), scale);
            vst1q_f32(dst_r + dst_idx + 4, r_hi_f32);
            
            // ─────────────────────────────────────────────────────
            // Process G channel
            // ─────────────────────────────────────────────────────
            uint16x8_t g_u16 = vmovl_u8(g_u8);
            
            uint32x4_t g_lo_u32 = vmovl_u16(vget_low_u16(g_u16));
            float32x4_t g_lo_f32 = vmulq_f32(vcvtq_f32_u32(g_lo_u32), scale);
            vst1q_f32(dst_g + dst_idx, g_lo_f32);
            
            uint32x4_t g_hi_u32 = vmovl_u16(vget_high_u16(g_u16));
            float32x4_t g_hi_f32 = vmulq_f32(vcvtq_f32_u32(g_hi_u32), scale);
            vst1q_f32(dst_g + dst_idx + 4, g_hi_f32);
            
            // ─────────────────────────────────────────────────────
            // Process B channel
            // ─────────────────────────────────────────────────────
            uint16x8_t b_u16 = vmovl_u8(b_u8);
            
            uint32x4_t b_lo_u32 = vmovl_u16(vget_low_u16(b_u16));
            float32x4_t b_lo_f32 = vmulq_f32(vcvtq_f32_u32(b_lo_u32), scale);
            vst1q_f32(dst_b + dst_idx, b_lo_f32);
            
            uint32x4_t b_hi_u32 = vmovl_u16(vget_high_u16(b_u16));
            float32x4_t b_hi_f32 = vmulq_f32(vcvtq_f32_u32(b_hi_u32), scale);
            vst1q_f32(dst_b + dst_idx + 4, b_hi_f32);
        }
        
        // Process remaining pixels (scalar)
        for (; x < width; ++x) {
            const int dst_x = x + pad_x_;
            const int dst_idx = dst_y * input_width_ + dst_x;
            const int src_idx = x * 3;
            
            const int r_src = is_bgr ? 2 : 0;
            const int b_src = is_bgr ? 0 : 2;
            
            dst_r[dst_idx] = src_row[src_idx + r_src] / 255.0f;
            dst_g[dst_idx] = src_row[src_idx + 1] / 255.0f;
            dst_b[dst_idx] = src_row[src_idx + b_src] / 255.0f;
        }
    }
}

void OptimizedPreprocessor::normalize_neon(
    const uint8_t* src,
    float* dst,
    int count
) {
    const float32x4_t scale = vdupq_n_f32(1.0f / 255.0f);
    
    int i = 0;
    
    // Process 16 bytes at a time
    for (; i + 16 <= count; i += 16) {
        // Load 16 uint8
        uint8x16_t pixels = vld1q_u8(src + i);
        
        // Split into two uint8x8
        uint8x8_t lo8 = vget_low_u8(pixels);
        uint8x8_t hi8 = vget_high_u8(pixels);
        
        // Process low 8 bytes
        uint16x8_t lo16 = vmovl_u8(lo8);
        
        uint32x4_t lo_lo32 = vmovl_u16(vget_low_u16(lo16));
        uint32x4_t lo_hi32 = vmovl_u16(vget_high_u16(lo16));
        
        float32x4_t f0 = vmulq_f32(vcvtq_f32_u32(lo_lo32), scale);
        float32x4_t f1 = vmulq_f32(vcvtq_f32_u32(lo_hi32), scale);
        
        vst1q_f32(dst + i + 0, f0);
        vst1q_f32(dst + i + 4, f1);
        
        // Process high 8 bytes
        uint16x8_t hi16 = vmovl_u8(hi8);
        
        uint32x4_t hi_lo32 = vmovl_u16(vget_low_u16(hi16));
        uint32x4_t hi_hi32 = vmovl_u16(vget_high_u16(hi16));
        
        float32x4_t f2 = vmulq_f32(vcvtq_f32_u32(hi_lo32), scale);
        float32x4_t f3 = vmulq_f32(vcvtq_f32_u32(hi_hi32), scale);
        
        vst1q_f32(dst + i + 8, f2);
        vst1q_f32(dst + i + 12, f3);
    }
    
    // Process remaining
    for (; i < count; ++i) {
        dst[i] = src[i] / 255.0f;
    }
}

#endif // USE_NEON

// ─────────────────────────────────────────────────────────────────
// iOS Accelerate Framework
// ─────────────────────────────────────────────────────────────────

#if USE_ACCELERATE

void OptimizedPreprocessor::resize_vimage(
    const uint8_t* src, int src_w, int src_h,
    uint8_t* dst, int dst_w, int dst_h,
    int channels
) {
    if (channels == 4) {
        // RGBA/BGRA
        vImage_Buffer srcBuffer = {
            .data = const_cast<uint8_t*>(src),
            .height = static_cast<vImagePixelCount>(src_h),
            .width = static_cast<vImagePixelCount>(src_w),
            .rowBytes = static_cast<size_t>(src_w * 4)
        };
        
        vImage_Buffer dstBuffer = {
            .data = dst,
            .height = static_cast<vImagePixelCount>(dst_h),
            .width = static_cast<vImagePixelCount>(dst_w),
            .rowBytes = static_cast<size_t>(dst_w * 4)
        };
        
        vImageScale_ARGB8888(&srcBuffer, &dstBuffer, nullptr, kvImageNoFlags);
    }
    else if (channels == 3) {
        // RGB - vImage has no native RGB, must convert or use planar
        // Fallback to fast software resize
        resize_fast(src, src_w, src_h, channels, dst, dst_w, dst_h);
    }
}

#endif // USE_ACCELERATE

} // namespace detector
```

### 10.5. ImageNet Normalization (với Mean/Std)

```cpp
// imagenet_normalize.hpp

#pragma once
#include <cstdint>
#include <array>

#if defined(__ARM_NEON) || defined(__ARM_NEON__)
#include <arm_neon.h>
#define USE_NEON 1
#else
#define USE_NEON 0
#endif

namespace detector {

/**
 * ImageNet normalization: (pixel/255 - mean) / std
 * 
 * Default values:
 *   mean = [0.485, 0.456, 0.406]
 *   std  = [0.229, 0.224, 0.225]
 */
class ImageNetNormalizer {
public:
    ImageNetNormalizer(
        std::array<float, 3> mean = {0.485f, 0.456f, 0.406f},
        std::array<float, 3> std = {0.229f, 0.224f, 0.225f}
    );
    
    /**
     * Normalize HWC uint8 image to CHW float tensor với ImageNet stats.
     */
    void normalize(
        const uint8_t* src,     // HWC, RGB, uint8
        float* dst,             // CHW, RGB, float
        int width, int height,
        int src_stride = 0      // 0 = width * 3
    );

private:
    // Pre-computed: scale = 1.0 / (255.0 * std)
    std::array<float, 3> scale_;
    
    // Pre-computed: offset = -mean / std
    std::array<float, 3> offset_;
    
#if USE_NEON
    float32x4_t scale_r_, scale_g_, scale_b_;
    float32x4_t offset_r_, offset_g_, offset_b_;
#endif
};

} // namespace detector
```

```cpp
// imagenet_normalize.cpp

#include "imagenet_normalize.hpp"

namespace detector {

ImageNetNormalizer::ImageNetNormalizer(
    std::array<float, 3> mean,
    std::array<float, 3> std
) {
    // Pre-compute to avoid per-pixel calculation
    // normalized = (pixel/255 - mean) / std
    //            = pixel / (255 * std) - mean / std
    //            = pixel * scale + offset
    
    for (int i = 0; i < 3; ++i) {
        scale_[i] = 1.0f / (255.0f * std[i]);
        offset_[i] = -mean[i] / std[i];
    }
    
#if USE_NEON
    scale_r_ = vdupq_n_f32(scale_[0]);
    scale_g_ = vdupq_n_f32(scale_[1]);
    scale_b_ = vdupq_n_f32(scale_[2]);
    
    offset_r_ = vdupq_n_f32(offset_[0]);
    offset_g_ = vdupq_n_f32(offset_[1]);
    offset_b_ = vdupq_n_f32(offset_[2]);
#endif
}

void ImageNetNormalizer::normalize(
    const uint8_t* src,
    float* dst,
    int width, int height,
    int src_stride
) {
    if (src_stride == 0) {
        src_stride = width * 3;
    }
    
    const int plane_size = width * height;
    float* dst_r = dst;
    float* dst_g = dst + plane_size;
    float* dst_b = dst + plane_size * 2;
    
#if USE_NEON
    for (int y = 0; y < height; ++y) {
        const uint8_t* row = src + y * src_stride;
        const int row_offset = y * width;
        
        int x = 0;
        
        // NEON: Process 8 pixels at a time
        for (; x + 8 <= width; x += 8) {
            // Load and deinterleave RGB
            uint8x8x3_t rgb = vld3_u8(row + x * 3);
            
            // R channel
            uint16x8_t r16 = vmovl_u8(rgb.val[0]);
            float32x4_t r_lo = vcvtq_f32_u32(vmovl_u16(vget_low_u16(r16)));
            float32x4_t r_hi = vcvtq_f32_u32(vmovl_u16(vget_high_u16(r16)));
            r_lo = vmlaq_f32(offset_r_, r_lo, scale_r_);  // r * scale + offset
            r_hi = vmlaq_f32(offset_r_, r_hi, scale_r_);
            vst1q_f32(dst_r + row_offset + x, r_lo);
            vst1q_f32(dst_r + row_offset + x + 4, r_hi);
            
            // G channel
            uint16x8_t g16 = vmovl_u8(rgb.val[1]);
            float32x4_t g_lo = vcvtq_f32_u32(vmovl_u16(vget_low_u16(g16)));
            float32x4_t g_hi = vcvtq_f32_u32(vmovl_u16(vget_high_u16(g16)));
            g_lo = vmlaq_f32(offset_g_, g_lo, scale_g_);
            g_hi = vmlaq_f32(offset_g_, g_hi, scale_g_);
            vst1q_f32(dst_g + row_offset + x, g_lo);
            vst1q_f32(dst_g + row_offset + x + 4, g_hi);
            
            // B channel
            uint16x8_t b16 = vmovl_u8(rgb.val[2]);
            float32x4_t b_lo = vcvtq_f32_u32(vmovl_u16(vget_low_u16(b16)));
            float32x4_t b_hi = vcvtq_f32_u32(vmovl_u16(vget_high_u16(b16)));
            b_lo = vmlaq_f32(offset_b_, b_lo, scale_b_);
            b_hi = vmlaq_f32(offset_b_, b_hi, scale_b_);
            vst1q_f32(dst_b + row_offset + x, b_lo);
            vst1q_f32(dst_b + row_offset + x + 4, b_hi);
        }
        
        // Scalar: Remaining pixels
        for (; x < width; ++x) {
            const int src_idx = x * 3;
            const int dst_idx = row_offset + x;
            
            dst_r[dst_idx] = row[src_idx + 0] * scale_[0] + offset_[0];
            dst_g[dst_idx] = row[src_idx + 1] * scale_[1] + offset_[1];
            dst_b[dst_idx] = row[src_idx + 2] * scale_[2] + offset_[2];
        }
    }
    
#else
    // Scalar fallback
    for (int y = 0; y < height; ++y) {
        const uint8_t* row = src + y * src_stride;
        const int row_offset = y * width;
        
        for (int x = 0; x < width; ++x) {
            const int src_idx = x * 3;
            const int dst_idx = row_offset + x;
            
            dst_r[dst_idx] = row[src_idx + 0] * scale_[0] + offset_[0];
            dst_g[dst_idx] = row[src_idx + 1] * scale_[1] + offset_[1];
            dst_b[dst_idx] = row[src_idx + 2] * scale_[2] + offset_[2];
        }
    }
#endif
}

} // namespace detector
```


### 10.6. Optimization Checklist

```
┌─────────────────────────────────────────────────────────────────┐
│                  PREPROCESSING OPTIMIZATION CHECKLIST           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MEMORY MANAGEMENT                                              │
│  ✅ Pre-allocate buffers (no malloc per frame)              │
│  ✅ Reuse tensors between frames                              │
│  ✅ 16-byte alignment cho SIMD                                 │
│                                                                 │
│  SIMD (ARM NEON)                                               │
│  ✅ Use vld3_u8 to deinterleave RGB                           │
│  ✅ Process 8-16 pixels mỗi iteration                          │
│  ✅ Use vmlaq_f32 for fused multiply-add                      │
│                                                                 │
│  MATH OPERATIONS                                                │
│  ✅ Multiplication instead of division (x * 0.00392 vs x / 255)   │
│  ✅ Pre-compute scale and offset                                │
│  ✅ Avoid branching in inner loop                           │
│                                                                 │
│  MEMORY ACCESS                                                  │
│  ✅ Process theo row (cache-friendly)                          │
│  ✅ Prefetch if needed (__builtin_prefetch)                      │
│  ✅ Avoid random access patterns                                │
│                                                                 │
│  PLATFORM-SPECIFIC                                              │
│  ✅ iOS: vImage, Accelerate, Metal                             │
│  ✅ Android: RenderScript, Vulkan Compute                      │
│  ✅ Consider GPU preprocessing if available sẵn                      │
│                                                                 │
│  RESIZE OPTIMIZATION                                            │
│  ✅ Nearest neighbor cho real-time (fastest)                   │
│  ✅ Bilinear cho quality/speed balance                         │
│  ✅ GPU resize when available                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 10.7. Config Option cho Optimization Level

```python
class OptimizationLevel(Enum):
    """Preprocessing optimization level."""
    NONE = "none"           # Naive implementation (portable)
    BASIC = "basic"         # Buffer reuse + row-wise ops
    SIMD = "simd"           # NEON/SSE intrinsics
    PLATFORM = "platform"   # Platform-specific (vImage, RenderScript)
    GPU = "gpu"             # GPU preprocessing (Metal, Vulkan)
```

```yaml
# model_config.yaml
preprocess:
  input_width: 640
  input_height: 640
  optimization_level: simd  # none | basic | simd | platform | gpu
  # ...
```

---

## 11. Entry Points

### 11.1. Main Entry Point

```python
# onnx_codegen/__main__.py

import sys


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] != '--gui':
        # CLI mode
        from .cli.main import main as cli_main
        cli_main()
    else:
        # GUI mode (default)
        from .gui.main import run_gui
        run_gui()


if __name__ == "__main__":
    main()
```

### 11.2. Setup.py

```python
# setup.py

from setuptools import setup, find_packages

setup(
    name="onnx-codegen",
    version="4.0.0",
    packages=find_packages(),
    install_requires=[
        "onnx>=1.14.0",
        "onnxruntime>=1.15.0",
        "PySide6>=6.5.0",
        "PyYAML>=6.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        "console_scripts": [
            "onnx-codegen=onnx_codegen.__main__:main",
        ],
        "gui_scripts": [
            "onnx-codegen-gui=onnx_codegen.gui.main:run_gui",
        ],
    },
    python_requires=">=3.9",
)
```

### 11.3. Error Handling

```python
# core/errors.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List


class ErrorCode(Enum):
    """Error codes for tool."""
    # Input errors (1xx)
    ONNX_NOT_FOUND = 101
    ONNX_INVALID = 102
    PYTHON_CODE_NOT_FOUND = 103
    PYTHON_CODE_INVALID = 104
    IMAGE_NOT_FOUND = 105
    IMAGE_INVALID = 106
    
    # Environment errors (2xx)
    OPENCV_NOT_FOUND = 201
    ONNXRUNTIME_NOT_FOUND = 202
    CMAKE_NOT_FOUND = 203
    COMPILER_NOT_FOUND = 204
    NDK_NOT_FOUND = 205
    XCODE_NOT_FOUND = 206
    
    # Parse errors (3xx)
    PYTHON_PARSE_FAILED = 301
    CONFIG_INVALID = 302
    
    # Generation errors (4xx)
    GENERATION_FAILED = 401
    OUTPUT_DIR_NOT_WRITABLE = 402
    
    # Verification errors (5xx)
    COMPILE_FAILED = 501
    RUN_FAILED = 502
    VERIFICATION_MISMATCH = 503
    VERIFICATION_TIMEOUT = 504


@dataclass
class ONNXCodeGenError(Exception):
    """Base exception for ONNX CodeGen."""
    code: ErrorCode
    message: str
    details: Optional[str] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
    
    def __str__(self):
        return f"[{self.code.name}] {self.message}"
    
    def to_dict(self):
        return {
            "code": self.code.value,
            "name": self.code.name,
            "message": self.message,
            "details": self.details,
            "suggestions": self.suggestions
        }


# Predefined errors with suggestions
ERROR_TEMPLATES = {
    ErrorCode.ONNX_NOT_FOUND: {
        "message": "ONNX file not found",
        "suggestions": ["Check file path", "Ensure file has .onnx extension"]
    },
    ErrorCode.OPENCV_NOT_FOUND: {
        "message": "OpenCV not found",
        "suggestions": [
            "Install OpenCV: sudo apt install libopencv-dev",
            "Or use stb_image mode (no dependencies)"
        ]
    },
    ErrorCode.CMAKE_NOT_FOUND: {
        "message": "CMake not found",
        "suggestions": ["Install CMake: sudo apt install cmake"]
    },
    ErrorCode.COMPILE_FAILED: {
        "message": "C++ compilation failed",
        "suggestions": [
            "Check compiler is installed: g++ --version",
            "Check CMakeLists.txt syntax",
            "Check include paths for ONNX Runtime and OpenCV"
        ]
    },
    ErrorCode.VERIFICATION_MISMATCH: {
        "message": "Python and C++ results do not match",
        "suggestions": [
            "Check preprocessing config (resize, normalize, color format)",
            "Check postprocessing config (NMS threshold, confidence)",
            "Try with different test image"
        ]
    },
}


def create_error(code: ErrorCode, details: str = None) -> ONNXCodeGenError:
    """Create error from template."""
    template = ERROR_TEMPLATES.get(code, {"message": "Unknown error", "suggestions": []})
    return ONNXCodeGenError(
        code=code,
        message=template["message"],
        details=details,
        suggestions=template["suggestions"]
    )


class ErrorHandler:
    """Handler to display errors in GUI."""
    
    @staticmethod
    def format_for_gui(error: ONNXCodeGenError) -> str:
        """Format error for GUI display."""
        lines = [f"❌ {error.message}"]
        if error.details:
            lines.append(f"\nDetails: {error.details}")
        if error.suggestions:
            lines.append("\n💡 Suggestions:")
            for s in error.suggestions:
                lines.append(f"  • {s}")
        return "\n".join(lines)
    
    @staticmethod
    def format_for_cli(error: ONNXCodeGenError) -> str:
        """Format error for CLI output."""
        lines = [f"Error [{error.code.name}]: {error.message}"]
        if error.details:
            lines.append(f"  {error.details}")
        if error.suggestions:
            lines.append("Suggestions:")
            for s in error.suggestions:
                lines.append(f"  - {s}")
        return "\n".join(lines)
```

---

## 12. Summary

### 12.1. Two-Phase Workflow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│  TWO-PHASE WORKFLOW                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE 1: C++ Core (Required)                                  │
│  ─────────────────────────────                                  │
│  Step 1: Input      → ONNX + Python code (optional)            │
│  Step 2: Configure  → Preprocessing, C++ options               │
│  Step 3: Verify     → Test C++ on PC                         │
│  Step 4: Generate   → Generate C++ core code                       │
│                                                                 │
│  Output:                                                        │
│  📁 output/cpp/                                                 │
│  ├── detector.hpp/cpp                                          │
│  ├── verify_single.cpp                                         │
│  ├── CMakeLists.txt                                            │
│  └── README.md                                                  │
│                                                                 │
│  → User can STOP here if only need PC                      │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  PHASE 2: Mobile Wrapper (Optional)                            │
│  ──────────────────────────────────                             │
│  Step 5: Mobile Config  → Select platform, use case              │
│  Step 6: Generate       → Generate wrapper code                    │
│                                                                 │
│  Output (added):                                            │
│  📁 output/android/ hoặc output/ios/                           │
│  ├── jni/ hoặc bridge/                                         │
│  ├── kotlin/ hoặc swift/                                       │
│  └── README.md                                                  │
│                                                                 │
│  LỢI ÍCH:                                                       │
│  • C++ verified independently first                               │
│  • Mobile code is just wrapper, no need to re-verify logic     │
│  • Clear: C++ = logic, Mobile = integration                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 12.2. Code Generation Summary

```
┌─────────────────────────────────────────────────────────────────┐
│  CODE GENERATION SUMMARY                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE 1: C++ Core (always generated)                          │
│  ─────────────────────────────────────                          │
│  • detector.hpp/cpp      - Core detection logic                │
│  • verify_single.cpp     - Test with 1 image                      │
│  • CMakeLists.txt        - Build config                        │
│  • README.md             - Instructions build & extend           │
│                                                                 │
│  PHASE 2: Mobile Wrapper (optional)                            │
│  ──────────────────────────────────                             │
│                                                                 │
│  Android:                                                       │
│  ─────────                                                      │
│  • detector_jni.cpp      - JNI bridge                          │
│  • Detector.kt           - Kotlin wrapper                      │
│  • [UseCase].kt          - SingleImageVerifier /               │
│                            BatchVerifier /                     │
│                            CameraFrameAnalyzer                 │
│                                                                 │
│  iOS:                                                           │
│  ────                                                           │
│  • detector_ios.mm       - ObjC++ bridge                       │
│  • Detector.swift        - Swift wrapper                       │
│  • [UseCase].swift       - SingleImageVerifier /               │
│                            BatchVerifier /                     │
│                            CameraFrameProcessor                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 12.3. Dependencies Summary

```
┌─────────────────────────────────────────────────────────────────┐
│  DEPENDENCIES                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  REQUIRED (tool will not run/verify if missing):                  │
│  • Python >= 3.9 + packages (onnx, onnxruntime, PySide6, etc.) │
│  • CMake + C++ compiler                                        │
│  • ONNX Runtime C++ libs                                       │
│  • OpenCV C++ libs       → verify C++ code on PC            │
│                                                                 │
│  OPTIONAL (for mobile targets):                                │
│  • Android NDK           → generate/verify Android wrapper    │
│  • Android Emulator      → run Android code on PC           │
│  • Xcode (macOS only)    → generate/verify iOS wrapper        │
│                                                                 │
│  PLATFORM NOTES:                                                │
│  • Windows/Linux: Can generate + verify C++ and Android         │
│  • Windows/Linux: Can generate iOS but CANNOT verify     │
│  • macOS: Can generate + verify all platforms               │
│                                                                 │
│  Check: onnx-codegen --check-env                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 12.4. GUI Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  GUI WORKFLOW (2 PHASES, 6 STEPS)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE 1: C++ Core                                             │
│  ─────────────────                                              │
│  Step 1: INPUT                                                 │
│  • Select ONNX file (required)                                   │
│  • [Optional] Python code, Labels file                         │
│                                                                 │
│  Step 2: CONFIGURE                                             │
│  • Select C++ options (OpenCV / stb_image / Raw buffer)         │
│  • Adjust preprocessing/postprocessing config                  │
│                                                                 │
│  Step 3: VERIFY                                                │
│  • Import test image                                           │
│  • Run Python + C++ verification                              │
│  • Compare results                                            │
│                                                                 │
│  Step 4: GENERATE C++                                          │
│  • Generate C++ core code                                         │
│  • Preview and save                                            │
│  • → Can stop here                                        │
│                                                                 │
│  PHASE 2: Mobile Wrapper (Optional)                            │
│  ──────────────────────────────────                             │
│  Step 5: MOBILE CONFIG                                         │
│  • Select platform (Android / iOS)                              │
│  • Select use case (verify single image / folder / camera)           │
│                                                                 │
│  Step 6: GENERATE MOBILE                                       │
│  • Generate wrapper code (JNI/Swift)                              │
│  • Generate app code (Kotlin/Swift)                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 12.5. Files Structure

```
onnx_codegen/
├── core/                   # Logic (no UI dependency)
│   ├── analyzer.py        # ONNX analysis
│   ├── parser.py          # Python code parsing
│   ├── config.py          # Config schema
│   ├── generator.py       # Code generation
│   ├── environment.py     # Environment detection
│   └── verifier.py        # Verification logic
├── cli/                    # Command-line interface
├── gui/                    # PySide6 GUI
│   ├── widgets/           # Reusable widgets
│   ├── workers/           # Background threads
│   └── resources/         # Icons, styles
└── tests/                  # Unit tests
```

---

> **ONNX Code Generator v4**
> - **Goal**: Generate code inference C++ từ ONNX model
> - **Workflow**: 2 phases - C++ Core (required) + Mobile Wrapper (optional)
> - **Principle**: Verify C++ on PC first, mobile code is just wrapper
> - **Interfaces**: CLI + GUI (PySide6)
