"""
Config Editor Widget.

Allows user to edit preprocessing and postprocessing configuration.
"""

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
        QComboBox, QGroupBox, QFormLayout, QTabWidget
    )
    from PySide6.QtCore import Signal
except ImportError:
    print("Error: PySide6 not installed")
    import sys
    sys.exit(1)

from ...core.config import ModelConfig, ResizeMode, ColorFormat, PostprocessType


class ConfigEditorWidget(QWidget):
    """Widget for editing model configuration."""
    
    config_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        # Preprocessing tab
        prep_tab = self._create_preprocessing_tab()
        tabs.addTab(prep_tab, "Preprocessing")
        
        # Postprocessing tab
        post_tab = self._create_postprocessing_tab()
        tabs.addTab(post_tab, "Postprocessing")
        
        layout.addWidget(tabs)
    
    def _create_preprocessing_tab(self) -> QWidget:
        """Create preprocessing configuration tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Input size
        size_layout = QHBoxLayout()
        self.input_width_spin = QSpinBox()
        self.input_width_spin.setRange(32, 4096)
        self.input_width_spin.setValue(640)
        self.input_width_spin.valueChanged.connect(self._on_config_changed)
        
        self.input_height_spin = QSpinBox()
        self.input_height_spin.setRange(32, 4096)
        self.input_height_spin.setValue(640)
        self.input_height_spin.valueChanged.connect(self._on_config_changed)
        
        size_layout.addWidget(self.input_width_spin)
        size_layout.addWidget(QLabel("x"))
        size_layout.addWidget(self.input_height_spin)
        layout.addRow("Input Size (W x H):", size_layout)
        
        # Color format
        self.color_format_combo = QComboBox()
        self.color_format_combo.addItems(["RGB", "BGR"])
        self.color_format_combo.currentTextChanged.connect(self._on_config_changed)
        layout.addRow("Color Format:", self.color_format_combo)
        
        # Resize mode
        self.resize_mode_combo = QComboBox()
        self.resize_mode_combo.addItems(["resize", "letterbox", "crop"])
        self.resize_mode_combo.currentTextChanged.connect(self._on_config_changed)
        layout.addRow("Resize Mode:", self.resize_mode_combo)
        
        # Normalize
        self.normalize_check = QCheckBox()
        self.normalize_check.setChecked(True)
        self.normalize_check.stateChanged.connect(self._on_config_changed)
        layout.addRow("Normalize:", self.normalize_check)
        
        # Scale
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.0, 1.0)
        self.scale_spin.setSingleStep(0.001)
        self.scale_spin.setValue(1.0 / 255.0)
        self.scale_spin.setDecimals(6)
        self.scale_spin.valueChanged.connect(self._on_config_changed)
        layout.addRow("Scale:", self.scale_spin)
        
        # Mean
        mean_layout = QHBoxLayout()
        self.mean_r_spin = QDoubleSpinBox()
        self.mean_r_spin.setRange(-255.0, 255.0)
        self.mean_r_spin.setValue(0.0)
        self.mean_r_spin.valueChanged.connect(self._on_config_changed)
        
        self.mean_g_spin = QDoubleSpinBox()
        self.mean_g_spin.setRange(-255.0, 255.0)
        self.mean_g_spin.setValue(0.0)
        self.mean_g_spin.valueChanged.connect(self._on_config_changed)
        
        self.mean_b_spin = QDoubleSpinBox()
        self.mean_b_spin.setRange(-255.0, 255.0)
        self.mean_b_spin.setValue(0.0)
        self.mean_b_spin.valueChanged.connect(self._on_config_changed)
        
        mean_layout.addWidget(QLabel("R:"))
        mean_layout.addWidget(self.mean_r_spin)
        mean_layout.addWidget(QLabel("G:"))
        mean_layout.addWidget(self.mean_g_spin)
        mean_layout.addWidget(QLabel("B:"))
        mean_layout.addWidget(self.mean_b_spin)
        layout.addRow("Mean (R, G, B):", mean_layout)
        
        # Std
        std_layout = QHBoxLayout()
        self.std_r_spin = QDoubleSpinBox()
        self.std_r_spin.setRange(0.001, 10.0)
        self.std_r_spin.setValue(1.0)
        self.std_r_spin.valueChanged.connect(self._on_config_changed)
        
        self.std_g_spin = QDoubleSpinBox()
        self.std_g_spin.setRange(0.001, 10.0)
        self.std_g_spin.setValue(1.0)
        self.std_g_spin.valueChanged.connect(self._on_config_changed)
        
        self.std_b_spin = QDoubleSpinBox()
        self.std_b_spin.setRange(0.001, 10.0)
        self.std_b_spin.setValue(1.0)
        self.std_b_spin.valueChanged.connect(self._on_config_changed)
        
        std_layout.addWidget(QLabel("R:"))
        std_layout.addWidget(self.std_r_spin)
        std_layout.addWidget(QLabel("G:"))
        std_layout.addWidget(self.std_g_spin)
        std_layout.addWidget(QLabel("B:"))
        std_layout.addWidget(self.std_b_spin)
        layout.addRow("Std (R, G, B):", std_layout)
        
        return widget
    
    def _create_postprocessing_tab(self) -> QWidget:
        """Create postprocessing configuration tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Postprocess type
        self.postprocess_type_combo = QComboBox()
        self.postprocess_type_combo.addItems(["nms", "soft_nms", "threshold", "anchor_nms", "direct", "softmax"])
        self.postprocess_type_combo.currentTextChanged.connect(self._on_config_changed)
        layout.addRow("Postprocess Type:", self.postprocess_type_combo)
        
        # Confidence threshold
        self.conf_threshold_spin = QDoubleSpinBox()
        self.conf_threshold_spin.setRange(0.0, 1.0)
        self.conf_threshold_spin.setSingleStep(0.01)
        self.conf_threshold_spin.setValue(0.25)
        self.conf_threshold_spin.valueChanged.connect(self._on_config_changed)
        layout.addRow("Confidence Threshold:", self.conf_threshold_spin)
        
        # IoU threshold
        self.iou_threshold_spin = QDoubleSpinBox()
        self.iou_threshold_spin.setRange(0.0, 1.0)
        self.iou_threshold_spin.setSingleStep(0.01)
        self.iou_threshold_spin.setValue(0.45)
        self.iou_threshold_spin.valueChanged.connect(self._on_config_changed)
        layout.addRow("IoU Threshold:", self.iou_threshold_spin)
        
        # Max detections
        self.max_detections_spin = QSpinBox()
        self.max_detections_spin.setRange(1, 10000)
        self.max_detections_spin.setValue(300)
        self.max_detections_spin.valueChanged.connect(self._on_config_changed)
        layout.addRow("Max Detections:", self.max_detections_spin)
        
        # Num classes
        self.num_classes_spin = QSpinBox()
        self.num_classes_spin.setRange(1, 10000)
        self.num_classes_spin.setValue(80)
        self.num_classes_spin.valueChanged.connect(self._on_config_changed)
        layout.addRow("Number of Classes:", self.num_classes_spin)
        
        return widget
    
    def set_config(self, config: ModelConfig):
        """Set configuration to edit."""
        self._config = config
        
        # Update preprocessing
        self.input_width_spin.setValue(config.preprocess.input_width)
        self.input_height_spin.setValue(config.preprocess.input_height)
        self.color_format_combo.setCurrentText(config.preprocess.color_format.value.upper())
        self.resize_mode_combo.setCurrentText(config.preprocess.resize_mode.value)
        self.normalize_check.setChecked(config.preprocess.normalize)
        self.scale_spin.setValue(config.preprocess.scale)
        
        if len(config.preprocess.mean) >= 3:
            self.mean_r_spin.setValue(config.preprocess.mean[0])
            self.mean_g_spin.setValue(config.preprocess.mean[1])
            self.mean_b_spin.setValue(config.preprocess.mean[2])
        
        if len(config.preprocess.std) >= 3:
            self.std_r_spin.setValue(config.preprocess.std[0])
            self.std_g_spin.setValue(config.preprocess.std[1])
            self.std_b_spin.setValue(config.preprocess.std[2])
        
        # Update postprocessing
        self.postprocess_type_combo.setCurrentText(config.postprocess.type.value)
        self.conf_threshold_spin.setValue(config.postprocess.conf_threshold)
        self.iou_threshold_spin.setValue(config.postprocess.iou_threshold)
        self.max_detections_spin.setValue(config.postprocess.max_detections)
        self.num_classes_spin.setValue(config.postprocess.num_classes)
    
    def get_config(self) -> ModelConfig:
        """Get current configuration."""
        if self._config is None:
            from ...core.config import ModelConfig
            self._config = ModelConfig()
        
        # Update preprocessing
        self._config.preprocess.input_width = self.input_width_spin.value()
        self._config.preprocess.input_height = self.input_height_spin.value()
        self._config.preprocess.color_format = ColorFormat(self.color_format_combo.currentText().lower())
        self._config.preprocess.resize_mode = ResizeMode(self.resize_mode_combo.currentText())
        self._config.preprocess.normalize = self.normalize_check.isChecked()
        self._config.preprocess.scale = self.scale_spin.value()
        self._config.preprocess.mean = [
            self.mean_r_spin.value(),
            self.mean_g_spin.value(),
            self.mean_b_spin.value()
        ]
        self._config.preprocess.std = [
            self.std_r_spin.value(),
            self.std_g_spin.value(),
            self.std_b_spin.value()
        ]
        
        # Update postprocessing
        self._config.postprocess.type = PostprocessType(self.postprocess_type_combo.currentText())
        self._config.postprocess.conf_threshold = self.conf_threshold_spin.value()
        self._config.postprocess.iou_threshold = self.iou_threshold_spin.value()
        self._config.postprocess.max_detections = self.max_detections_spin.value()
        self._config.postprocess.num_classes = self.num_classes_spin.value()
        
        return self._config
    
    def _on_config_changed(self):
        """Handle configuration change."""
        self.config_changed.emit()

