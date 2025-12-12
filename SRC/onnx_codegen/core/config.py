"""
Configuration Schema and Builder.

Defines configuration data structures and builder to create configs from multiple sources.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from enum import Enum
import yaml
import json

from .analyzer import ONNXModelInfo
from .detector import DetectionResult
from .parser import ParseResult


class ResizeMode(Enum):
    RESIZE = "resize"
    LETTERBOX = "letterbox"
    CROP = "crop"


class ColorFormat(Enum):
    RGB = "rgb"
    BGR = "bgr"


class ImageInputMode(Enum):
    """Image input reading mode."""
    OPENCV = "opencv"
    RAW_BUFFER = "raw_buffer"
    ANDROID_NATIVE = "android"
    IOS_NATIVE = "ios"
    STB_IMAGE = "stb_image"


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
    image_input_mode: ImageInputMode = ImageInputMode.OPENCV
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
    target_platform: str = "pc"
    
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
        data['preprocess']['image_input_mode'] = self.preprocess.image_input_mode.value
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
            pre['image_input_mode'] = ImageInputMode(pre.get('image_input_mode', 'opencv'))
            data['preprocess'] = PreprocessConfig(**pre)
        
        if 'postprocess' in data:
            post = data['postprocess']
            post['type'] = PostprocessType(post.get('type', 'nms'))
            data['postprocess'] = PostprocessConfig(**post)
        
        return cls(**data)


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
    
    def __init__(self, onnx_info: ONNXModelInfo, 
                 parse_result: Optional[ParseResult] = None,
                 detection_result: Optional[DetectionResult] = None):
        self.onnx_info = onnx_info
        self.parse_result = parse_result
        self.detection_result = detection_result
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
        """Build config from Python code (Mode A)."""
        prep = self.parse_result.preprocessing
        post = self.parse_result.postprocessing
        
        config = ModelConfig()
        config.model_path = self.onnx_info.file_path
        config.source = "python_code"
        config.confidence_score = 0.95
        
        # Set I/O from ONNX
        if self.onnx_info.inputs:
            config.input_name = self.onnx_info.inputs[0].name
            config.input_shape = [d if isinstance(d, int) else 1 for d in self.onnx_info.inputs[0].shape]
        
        config.output_names = [o.name for o in self.onnx_info.outputs]
        config.output_shapes = [[d if isinstance(d, int) else 1 for d in o.shape] for o in self.onnx_info.outputs]
        
        # Set preprocessing from Python code
        if prep.input_size:
            config.preprocess.input_width = prep.input_size[1]
            config.preprocess.input_height = prep.input_size[0]
        
        if prep.color_format:
            config.preprocess.color_format = ColorFormat(prep.color_format.lower())
        
        if prep.resize_mode:
            config.preprocess.resize_mode = ResizeMode(prep.resize_mode.lower())
        
        if prep.normalize is not None:
            config.preprocess.normalize = prep.normalize
            if prep.scale:
                config.preprocess.scale = prep.scale
        
        if prep.mean:
            config.preprocess.mean = list(prep.mean)
        if prep.std:
            config.preprocess.std = list(prep.std)
        
        # Set postprocessing from Python code
        if post.conf_threshold is not None:
            config.postprocess.conf_threshold = post.conf_threshold
        if post.iou_threshold is not None:
            config.postprocess.iou_threshold = post.iou_threshold
        if post.num_classes is not None:
            config.postprocess.num_classes = post.num_classes
        
        if post.has_nms:
            config.postprocess.type = PostprocessType.NMS
        
        config.warnings = self.parse_result.warnings
        
        return BuildResult(
            config=config,
            confidence=0.95,
            source="python_code",
            warnings=self.parse_result.warnings,
            evidence=prep.evidence
        )
    
    def _build_from_heuristic(self) -> BuildResult:
        """Build config from ONNX heuristics (Mode B)."""
        config = ModelConfig()
        config.model_path = self.onnx_info.file_path
        config.source = "onnx_heuristic"
        
        # Set I/O from ONNX
        if self.onnx_info.inputs:
            config.input_name = self.onnx_info.inputs[0].name
            shape = self.onnx_info.inputs[0].shape
            # Extract input size, handling dynamic shapes
            if len(shape) == 4:
                if isinstance(shape[2], int) and shape[2] > 0:
                    config.preprocess.input_height = shape[2]
                if isinstance(shape[3], int) and shape[3] > 0:
                    config.preprocess.input_width = shape[3]
        
        config.output_names = [o.name for o in self.onnx_info.outputs]
        config.output_shapes = [[d if isinstance(d, int) else 1 for d in o.shape] for o in self.onnx_info.outputs]
        
        # Use detection result if available
        if self.detection_result:
            config.architecture = self.detection_result.architecture.name.lower()
            config.confidence_score = self.detection_result.confidence
            
            suggestions = self.detection_result.suggestions
            if "preprocessing" in suggestions:
                prep_sugg = suggestions["preprocessing"]
                if "color_format" in prep_sugg:
                    config.preprocess.color_format = ColorFormat(prep_sugg["color_format"].lower())
                if "resize_mode" in prep_sugg:
                    config.preprocess.resize_mode = ResizeMode(prep_sugg["resize_mode"].lower())
                if "mean" in prep_sugg:
                    config.preprocess.mean = prep_sugg["mean"]
                if "std" in prep_sugg:
                    config.preprocess.std = prep_sugg["std"]
            
            if "postprocessing" in suggestions:
                post_sugg = suggestions["postprocessing"]
                if "conf_threshold" in post_sugg:
                    config.postprocess.conf_threshold = post_sugg["conf_threshold"]
                if "iou_threshold" in post_sugg:
                    config.postprocess.iou_threshold = post_sugg["iou_threshold"]
                if "type" in post_sugg:
                    try:
                        config.postprocess.type = PostprocessType(post_sugg["type"])
                    except ValueError:
                        pass
                if "num_classes" in suggestions:
                    config.postprocess.num_classes = suggestions["num_classes"]
        
        # Infer num_classes from output shape if not set
        if config.postprocess.num_classes == 80 and config.output_shapes:
            try:
                output_shape = config.output_shapes[0]
                if len(output_shape) == 3:
                    if output_shape[1] < output_shape[2]:  # [1, 84, 8400]
                        config.postprocess.num_classes = max(1, output_shape[1] - 4)
                    else:  # [1, 25200, 85]
                        config.postprocess.num_classes = max(1, output_shape[2] - 5)
            except:
                pass
        
        confidence = self.detection_result.confidence if self.detection_result else 0.7
        
        return BuildResult(
            config=config,
            confidence=confidence,
            source="onnx_heuristic",
            warnings=self.warnings
        )

