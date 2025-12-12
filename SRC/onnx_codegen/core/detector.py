"""
Architecture Detection Module.

Detects model architecture from ONNX model using heuristics (Mode B).
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
from enum import Enum, auto

from .analyzer import ONNXModelInfo


class Architecture(Enum):
    """Supported model architectures."""
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
    """Architecture detection results."""
    architecture: Architecture
    confidence: float  # 0.0 - 1.0
    evidence: List[str]  # Reasons for conclusion
    suggestions: Dict[str, Any]  # Config suggestions


class ArchitectureDetector:
    """Detect architecture from ONNX model."""
    
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
                    # Handle dynamic shapes
                    h = input_shape[2] if isinstance(input_shape[2], int) else None
                    w = input_shape[3] if isinstance(input_shape[3], int) else None
                    typical = patterns["typical_input"]
                    if h == typical[0] and w == typical[1]:
                        score += 0.1
                        arch_evidence.append(f"Input size matches typical {arch.name}")
            
            scores[arch] = min(score, 1.0)
            evidence[arch] = arch_evidence
        
        # Select architecture with highest score
        if not scores:
            best_arch = Architecture.UNKNOWN
            best_score = 0.0
        else:
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
                # Try to infer num_classes from output shape
                try:
                    num_features = output_shapes[0][1] if isinstance(output_shapes[0][1], int) else None
                    if num_features:
                        suggestions["num_classes"] = num_features - 4
                except:
                    pass
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

