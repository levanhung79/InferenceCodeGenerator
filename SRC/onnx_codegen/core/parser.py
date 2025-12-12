"""
Python Code Parser.

Extracts preprocessing/postprocessing configuration from Python inference code.
"""

import ast
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from .errors import create_error, ErrorCode


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
    """Results from parsing Python code."""
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
    
    def __init__(self, code_path: str):
        self.code_path = Path(code_path)
        if not self.code_path.exists():
            raise create_error(ErrorCode.PYTHON_CODE_NOT_FOUND, f"File not found: {code_path}")
        
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
        """Extract preprocessing information."""
        prep = ParsedPreprocessing()
        
        # Extract input size
        match = self.PREPROCESS_PATTERNS["img_size"].search(self.code_content)
        if match:
            size = int(match.group(1) or match.group(2) or match.group(3))
            prep.input_size = (size, size)
            prep.evidence["input_size"] = match.group(0)
        
        # Extract resize mode
        if self.PREPROCESS_PATTERNS["letterbox"].search(self.code_content):
            prep.resize_mode = "letterbox"
        elif self.PREPROCESS_PATTERNS["resize_cv2"].search(self.code_content):
            prep.resize_mode = "resize"
        
        # Extract color format
        if self.PREPROCESS_PATTERNS["bgr2rgb"].search(self.code_content):
            prep.color_format = "RGB"
        elif self.PREPROCESS_PATTERNS["rgb2bgr"].search(self.code_content):
            prep.color_format = "BGR"
        
        # Extract normalization
        if self.PREPROCESS_PATTERNS["div_255"].search(self.code_content):
            prep.normalize = True
            prep.scale = 1.0 / 255.0
        
        # Extract channel order
        if self.PREPROCESS_PATTERNS["transpose_chw"].search(self.code_content):
            prep.channel_order = "CHW"
        elif self.PREPROCESS_PATTERNS["permute_chw"].search(self.code_content):
            prep.channel_order = "CHW"
        
        return prep
    
    def _extract_postprocessing(self) -> ParsedPostprocessing:
        """Extract postprocessing information."""
        post = ParsedPostprocessing()
        
        # Extract NMS
        if (self.POSTPROCESS_PATTERNS["nms_cv2"].search(self.code_content) or
            self.POSTPROCESS_PATTERNS["nms_torchvision"].search(self.code_content) or
            self.POSTPROCESS_PATTERNS["nms_custom"].search(self.code_content)):
            post.has_nms = True
        
        # Extract confidence threshold
        match = self.POSTPROCESS_PATTERNS["conf_threshold"].search(self.code_content)
        if match:
            post.conf_threshold = float(match.group(1))
            post.evidence["conf_threshold"] = match.group(0)
        
        # Extract IoU threshold
        match = self.POSTPROCESS_PATTERNS["iou_threshold"].search(self.code_content)
        if match:
            post.iou_threshold = float(match.group(1))
            post.evidence["iou_threshold"] = match.group(0)
        
        # Extract num_classes
        match = self.POSTPROCESS_PATTERNS["num_classes"].search(self.code_content)
        if match:
            post.num_classes = int(match.group(1) or match.group(2) or match.group(3))
        
        return post
    
    def _extract_model_path(self) -> Optional[str]:
        """Extract model path from code."""
        patterns = [
            re.compile(r"model\s*=\s*['\"]([^'\"]+)['\"]"),
            re.compile(r"load\s*\(['\"]([^'\"]+)['\"]"),
            re.compile(r"\.onnx"),
        ]
        
        for pattern in patterns:
            match = pattern.search(self.code_content)
            if match:
                return match.group(1) if match.groups() else None
        
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

