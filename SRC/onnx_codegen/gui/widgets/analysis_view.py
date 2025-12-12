"""
Analysis View Widget.

Displays ONNX model analysis results and architecture detection.
"""

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QTextEdit, QGroupBox, QTableWidget, QTableWidgetItem,
        QHeaderView
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont
except ImportError:
    print("Error: PySide6 not installed")
    import sys
    sys.exit(1)

from ...core.analyzer import ONNXModelInfo
from ...core.detector import DetectionResult


class AnalysisViewWidget(QWidget):
    """Widget to display model analysis results."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        # Model info section
        model_group = QGroupBox("Model Information")
        model_layout = QVBoxLayout()
        
        self.model_info_text = QTextEdit()
        self.model_info_text.setReadOnly(True)
        self.model_info_text.setMaximumHeight(150)
        model_layout.addWidget(self.model_info_text)
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Architecture detection section
        arch_group = QGroupBox("Architecture Detection")
        arch_layout = QVBoxLayout()
        
        self.arch_label = QLabel("No model analyzed yet")
        self.arch_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        arch_layout.addWidget(self.arch_label)
        
        self.confidence_label = QLabel()
        arch_layout.addWidget(self.confidence_label)
        
        self.evidence_text = QTextEdit()
        self.evidence_text.setReadOnly(True)
        self.evidence_text.setMaximumHeight(100)
        arch_layout.addWidget(QLabel("Evidence:"))
        arch_layout.addWidget(self.evidence_text)
        
        arch_group.setLayout(arch_layout)
        layout.addWidget(arch_group)
        
        # Input/Output info
        io_group = QGroupBox("Input/Output Information")
        io_layout = QVBoxLayout()
        
        self.io_table = QTableWidget()
        self.io_table.setColumnCount(4)
        self.io_table.setHorizontalHeaderLabels(["Name", "Shape", "Type", "Dynamic"])
        self.io_table.horizontalHeader().setStretchLastSection(True)
        self.io_table.setMaximumHeight(200)
        io_layout.addWidget(self.io_table)
        
        io_group.setLayout(io_layout)
        layout.addWidget(io_group)
        
        layout.addStretch()
    
    def set_model_info(self, model_info: ONNXModelInfo):
        """Set model information to display."""
        info_lines = [
            f"File: {model_info.file_path}",
            f"Size: {model_info.file_size_mb:.2f} MB",
            f"IR Version: {model_info.ir_version}",
            f"Opset Version: {model_info.opset_version}",
            f"Producer: {model_info.producer_name} {model_info.producer_version}",
            f"Nodes: {model_info.num_nodes}",
            f"Operators: {', '.join(model_info.operators[:10])}" + 
            (f" (+{len(model_info.operators) - 10} more)" if len(model_info.operators) > 10 else ""),
        ]
        
        if model_info.has_dynamic_shape:
            info_lines.append("⚠️ Warning: Model has dynamic input shapes")
        
        self.model_info_text.setText("\n".join(info_lines))
        
        # Update I/O table
        self._update_io_table(model_info)
    
    def set_detection_result(self, detection: DetectionResult):
        """Set architecture detection results."""
        arch_name = detection.architecture.name
        confidence = detection.confidence
        
        # Set architecture label with color based on confidence
        if confidence >= 0.7:
            color = "#4CAF50"  # Green
        elif confidence >= 0.5:
            color = "#FF9800"  # Orange
        else:
            color = "#F44336"  # Red
        
        self.arch_label.setText(f"Detected: {arch_name}")
        self.arch_label.setStyleSheet(
            f"font-size: 14px; font-weight: bold; padding: 5px; color: {color};"
        )
        
        # Set confidence
        confidence_text = f"Confidence: {confidence:.1%}"
        if confidence < 0.5:
            confidence_text += " ⚠️ Low confidence - review recommended"
        self.confidence_label.setText(confidence_text)
        
        # Set evidence
        if detection.evidence:
            self.evidence_text.setText("\n".join(f"• {e}" for e in detection.evidence))
        else:
            self.evidence_text.setText("No evidence available")
    
    def _update_io_table(self, model_info: ONNXModelInfo):
        """Update I/O information table."""
        # Count total rows needed
        total_rows = len(model_info.inputs) + len(model_info.outputs)
        self.io_table.setRowCount(total_rows)
        
        row = 0
        
        # Add inputs
        for inp in model_info.inputs:
            self.io_table.setItem(row, 0, QTableWidgetItem(f"INPUT: {inp.name}"))
            shape_str = str(inp.shape).replace("'", "")
            self.io_table.setItem(row, 1, QTableWidgetItem(shape_str))
            self.io_table.setItem(row, 2, QTableWidgetItem(str(inp.dtype)))
            self.io_table.setItem(row, 3, QTableWidgetItem("Yes" if inp.is_dynamic else "No"))
            row += 1
        
        # Add outputs
        for out in model_info.outputs:
            self.io_table.setItem(row, 0, QTableWidgetItem(f"OUTPUT: {out.name}"))
            shape_str = str(out.shape).replace("'", "")
            self.io_table.setItem(row, 1, QTableWidgetItem(shape_str))
            self.io_table.setItem(row, 2, QTableWidgetItem(str(out.dtype)))
            self.io_table.setItem(row, 3, QTableWidgetItem("Yes" if out.is_dynamic else "No"))
            row += 1
        
        self.io_table.resizeColumnsToContents()
    
    def clear(self):
        """Clear all displayed information."""
        self.model_info_text.clear()
        self.arch_label.setText("No model analyzed yet")
        self.confidence_label.clear()
        self.evidence_text.clear()
        self.io_table.setRowCount(0)

