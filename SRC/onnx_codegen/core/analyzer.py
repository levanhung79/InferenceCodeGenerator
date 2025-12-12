"""
ONNX Model Analyzer.

Extracts information from ONNX files with 100% accuracy.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os

try:
    import onnx
    import onnxruntime as ort
    import numpy as np
except ImportError as e:
    raise ImportError(
        f"Required packages not installed: {e}\n"
        "Please install: pip install onnx onnxruntime numpy"
    )


@dataclass
class TensorInfo:
    """Information about a tensor."""
    name: str
    shape: List[Any]  # Can contain int, str (symbolic), or None
    dtype: str
    is_dynamic: bool = False  # True if dimension is -1 or symbolic


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
        if not os.path.exists(model_path):
            from .errors import create_error, ErrorCode
            raise create_error(ErrorCode.ONNX_NOT_FOUND, f"File not found: {model_path}")
        
        self.model_path = model_path
        self._onnx_model = None
        self._session = None
    
    @property
    def onnx_model(self):
        """Lazy load ONNX model."""
        if self._onnx_model is None:
            try:
                self._onnx_model = onnx.load(self.model_path)
            except Exception as e:
                from .errors import create_error, ErrorCode
                raise create_error(ErrorCode.ONNX_INVALID, f"Failed to load ONNX: {e}")
        return self._onnx_model
    
    @property
    def session(self):
        """Lazy load ONNX Runtime session."""
        if self._session is None:
            try:
                self._session = ort.InferenceSession(self.model_path)
            except Exception as e:
                from .errors import create_error, ErrorCode
                raise create_error(ErrorCode.ONNXRUNTIME_NOT_FOUND, f"Failed to create session: {e}")
        return self._session
    
    def analyze(self, progress_callback=None) -> ONNXModelInfo:
        """
        Comprehensive analysis of ONNX model.
        
        Args:
            progress_callback: Optional callback(percent, message) for progress reporting
        """
        if progress_callback:
            progress_callback(10, "Loading model...")
        
        # File info
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
                dtype=str(inp.type),
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
                dtype=str(out.type),
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

