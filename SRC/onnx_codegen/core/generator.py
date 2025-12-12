"""
Code Generator Module.

Generates C++ code from ModelConfig.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from .config import ModelConfig, ImageInputMode
from .errors import create_error, ErrorCode


class TargetPlatform(Enum):
    """Target platform for code generation."""
    PC_OPENCV = "pc_opencv"
    PC_STB = "pc_stb"
    PC_RAW = "pc_raw"
    ANDROID = "android"
    IOS = "ios"


class UseCase(Enum):
    """Use case for mobile code."""
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
    """Results from code generation."""
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
        
        # Load class names if available
        self.class_names = config.class_names if config.class_names else []
    
    def generate(self, 
                 platform: TargetPlatform,
                 output_dir: str,
                 use_case: Optional[UseCase] = None,
                 progress_callback=None) -> GenerationResult:
        """
        Generate code for target platform.
        
        Args:
            platform: Target platform
            output_dir: Output folder
            use_case: Use case (for mobile)
            progress_callback: Optional callback(percent, message)
        """
        result = GenerationResult(success=True, output_dir=output_dir)
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            if platform == TargetPlatform.PC_OPENCV:
                self._generate_pc_opencv(output_dir, result, progress_callback)
            elif platform == TargetPlatform.PC_STB:
                self._generate_pc_stb(output_dir, result, progress_callback)
            elif platform == TargetPlatform.ANDROID:
                self._generate_android(output_dir, use_case or UseCase.CAMERA, result, progress_callback)
            elif platform == TargetPlatform.IOS:
                self._generate_ios(output_dir, use_case or UseCase.CAMERA, result, progress_callback)
            else:
                result.success = False
                result.errors.append(f"Unsupported platform: {platform}")
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Generation failed: {str(e)}")
        
        return result
    
    def _generate_pc_opencv(self, output_dir: str, result: GenerationResult, callback):
        """Generate PC code with OpenCV."""
        if callback:
            callback(10, "Generating detector.hpp...")
        
        detector_hpp = self._render_detector_hpp(ImageInputMode.OPENCV)
        result.files.append(GeneratedFile(
            path=os.path.join(output_dir, "detector.hpp"),
            content=detector_hpp,
            description="Detector header file"
        ))
        
        if callback:
            callback(30, "Generating detector.cpp...")
        
        detector_cpp = self._render_detector_cpp(ImageInputMode.OPENCV)
        result.files.append(GeneratedFile(
            path=os.path.join(output_dir, "detector.cpp"),
            content=detector_cpp,
            description="Detector implementation"
        ))
        
        if callback:
            callback(50, "Generating verify_single.cpp...")
        
        verify_single = self._render_verify_single(ImageInputMode.OPENCV)
        result.files.append(GeneratedFile(
            path=os.path.join(output_dir, "verify_single.cpp"),
            content=verify_single,
            description="Single image verification"
        ))
        
        if callback:
            callback(70, "Generating CMakeLists.txt...")
        
        cmake = self._render_cmake(ImageInputMode.OPENCV)
        result.files.append(GeneratedFile(
            path=os.path.join(output_dir, "CMakeLists.txt"),
            content=cmake,
            description="CMake build configuration"
        ))
        
        if callback:
            callback(90, "Generating README.md...")
        
        readme = self._render_readme(ImageInputMode.OPENCV)
        result.files.append(GeneratedFile(
            path=os.path.join(output_dir, "README.md"),
            content=readme,
            description="Build and usage instructions"
        ))
        
        if callback:
            callback(100, "Done!")
        
        # Write all files
        for f in result.files:
            os.makedirs(os.path.dirname(f.path), exist_ok=True)
            with open(f.path, 'w', encoding='utf-8') as fp:
                fp.write(f.content)
    
    def _generate_pc_stb(self, output_dir: str, result: GenerationResult, callback):
        """Generate PC code with stb_image."""
        # TODO: Implement stb_image template
        result.warnings.append("stb_image mode not yet implemented")
    
    def _generate_android(self, output_dir: str, use_case: UseCase, 
                          result: GenerationResult, callback):
        """Generate Android code."""
        # TODO: Implement Android template
        result.warnings.append("Android generation not yet implemented")
    
    def _generate_ios(self, output_dir: str, use_case: UseCase,
                      result: GenerationResult, callback):
        """Generate iOS code."""
        # TODO: Implement iOS template
        result.warnings.append("iOS generation not yet implemented")
    
    def _render_detector_hpp(self, mode: ImageInputMode) -> str:
        """Render detector.hpp template."""
        input_name = self.config.input_name
        output_names = self.config.output_names[0] if self.config.output_names else "output"
        
        return f"""#pragma once

#include <onnxruntime_cxx_api.h>
#include <vector>
#include <string>
#include <memory>

namespace detector {{

struct Detection {{
    float x1, y1, x2, y2;
    float confidence;
    int class_id;
    std::string class_name;
}};

class Detector {{
public:
    Detector(const std::string& model_path,
             float conf_threshold = {self.config.postprocess.conf_threshold}f,
             float iou_threshold = {self.config.postprocess.iou_threshold}f);
    ~Detector();
    
    std::vector<Detection> detect(const std::string& image_path);
    
private:
    std::vector<float> preprocess(const cv::Mat& image);
    std::vector<Detection> postprocess(const std::vector<float>& output,
                                       int orig_width, int orig_height);
    std::vector<Detection> apply_nms(const std::vector<Detection>& candidates,
                                     float iou_threshold);
    float calculate_iou(const Detection& a, const Detection& b);
    std::string get_class_name(int class_id) const;
    
    std::unique_ptr<Ort::Env> env_;
    std::unique_ptr<Ort::Session> session_;
    
    int input_width_ = {self.config.preprocess.input_width};
    int input_height_ = {self.config.preprocess.input_height};
    float conf_threshold_;
    float iou_threshold_;
    int num_classes_ = {self.config.postprocess.num_classes};
    std::vector<std::string> class_names_;
}};

}} // namespace detector
"""
    
    def _render_detector_cpp(self, mode: ImageInputMode) -> str:
        """Render detector.cpp template."""
        input_name = self.config.input_name
        output_name = self.config.output_names[0] if self.config.output_names else "output"
        color_format = self.config.preprocess.color_format.value.upper()
        resize_mode = self.config.preprocess.resize_mode.value
        normalize = "true" if self.config.preprocess.normalize else "false"
        scale = self.config.preprocess.scale
        mean = f"{{{', '.join(map(str, self.config.preprocess.mean))}}}"
        std = f"{{{', '.join(map(str, self.config.preprocess.std))}}}"
        
        return f"""#include "detector.hpp"
#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <algorithm>
#include <stdexcept>
#include <cmath>
#include <numeric>

namespace detector {{

Detector::Detector(const std::string& model_path,
                   float conf_threshold,
                   float iou_threshold)
    : conf_threshold_(conf_threshold), iou_threshold_(iou_threshold) {{
    
    env_ = std::make_unique<Ort::Env>(ORT_LOGGING_LEVEL_WARNING, "Detector");
    Ort::SessionOptions options;
    options.SetIntraOpNumThreads(4);
    options.SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_ENABLE_ALL);
    
    session_ = std::make_unique<Ort::Session>(*env_, model_path.c_str(), options);
    
    // Initialize class names
    class_names_ = {{
{self._render_class_names()}
    }};
}}

Detector::~Detector() = default;

std::vector<float> Detector::preprocess(const cv::Mat& image) {{
    cv::Mat resized;
    
    // Resize
    if ("{resize_mode}" == "letterbox") {{
        // Letterbox resize
        float scale = std::min(static_cast<float>(input_width_) / image.cols,
                               static_cast<float>(input_height_) / image.rows);
        int new_w = static_cast<int>(image.cols * scale);
        int new_h = static_cast<int>(image.rows * scale);
        
        cv::resize(image, resized, cv::Size(new_w, new_h));
        
        int pad_w = input_width_ - new_w;
        int pad_h = input_height_ - new_h;
        int pad_left = pad_w / 2;
        int pad_top = pad_h / 2;
        
        cv::copyMakeBorder(resized, resized, pad_top, pad_h - pad_top,
                          pad_left, pad_w - pad_left, cv::BORDER_CONSTANT,
                          cv::Scalar(114, 114, 114));
    }} else {{
        cv::resize(image, resized, cv::Size(input_width_, input_height_));
    }}
    
    // Color conversion
    cv::Mat rgb;
    if ("{color_format}" == "RGB") {{
        cv::cvtColor(resized, rgb, cv::COLOR_BGR2RGB);
    }} else {{
        rgb = resized;
    }}
    
    // Normalize and convert to float
    cv::Mat blob;
    rgb.convertTo(blob, CV_32F, {scale}, 0);
    
    // Subtract mean and divide by std
    std::vector<cv::Mat> channels;
    cv::split(blob, channels);
    float mean[] = {mean};
    float std[] = {std};
    for (int i = 0; i < 3; ++i) {{
        channels[i] = (channels[i] - mean[i]) / std[i];
    }}
    
    // Convert HWC to CHW (NCHW format for ONNX)
    // Flatten to vector in NCHW format: [C, H, W]
    std::vector<float> input_data;
    input_data.reserve(3 * input_height_ * input_width_);
    
    for (int c = 0; c < 3; ++c) {{
        for (int h = 0; h < input_height_; ++h) {{
            for (int w = 0; w < input_width_; ++w) {{
                input_data.push_back(channels[c].at<float>(h, w));
            }}
        }}
    }}
    
    return input_data;
}}

std::vector<Detection> Detector::postprocess(const std::vector<float>& output,
                                             int orig_width, int orig_height) {{
    std::vector<Detection> detections;
    
    // Determine output shape
    // YOLOv8: [1, num_features, num_anchors] where num_features = 4 + num_classes
    // YOLOv5: [1, num_anchors, num_features] where num_features = 4 + num_classes
    size_t output_size = output.size();
    int num_features = num_classes_ + 4;
    
    if (output_size % num_features != 0) {{
        return detections; // Invalid output shape
    }}
    
    int num_anchors = output_size / num_features;
    bool is_yolov8_format = false; // Assume YOLOv5 format by default
    
    // Try to detect format: if num_features < num_anchors, likely YOLOv8 format
    if (num_features < num_anchors) {{
        is_yolov8_format = true;
    }}
    
    // Parse detections
    std::vector<Detection> candidates;
    
    for (int i = 0; i < num_anchors; ++i) {{
        float cx, cy, w, h;
        float max_conf = 0.0f;
        int best_class = 0;
        
        if (is_yolov8_format) {{
            // YOLOv8: [1, num_features, num_anchors]
            // Access: output[feature_idx * num_anchors + anchor_idx]
            cx = output[0 * num_anchors + i];
            cy = output[1 * num_anchors + i];
            w = output[2 * num_anchors + i];
            h = output[3 * num_anchors + i];
            
            // Find best class
            for (int c = 0; c < num_classes_; ++c) {{
                float conf = output[(4 + c) * num_anchors + i];
                if (conf > max_conf) {{
                    max_conf = conf;
                    best_class = c;
                }}
            }}
        }} else {{
            // YOLOv5: [1, num_anchors, num_features]
            // Access: output[anchor_idx * num_features + feature_idx]
            int offset = i * num_features;
            cx = output[offset];
            cy = output[offset + 1];
            w = output[offset + 2];
            h = output[offset + 3];
            
            // Find best class
            for (int c = 0; c < num_classes_; ++c) {{
                float conf = output[offset + 4 + c];
                if (conf > max_conf) {{
                    max_conf = conf;
                    best_class = c;
                }}
            }}
        }}
        
        // Apply confidence threshold
        if (max_conf < conf_threshold_) {{
            continue;
        }}
        
        // Convert cx,cy,w,h to x1,y1,x2,y2
        float x1 = cx - w / 2.0f;
        float y1 = cy - h / 2.0f;
        float x2 = cx + w / 2.0f;
        float y2 = cy + h / 2.0f;
        
        // Scale to original image size (assuming letterbox preprocessing)
        float scale = std::min(static_cast<float>(input_width_) / orig_width,
                              static_cast<float>(input_height_) / orig_height);
        float pad_x = (input_width_ - orig_width * scale) / 2.0f;
        float pad_y = (input_height_ - orig_height * scale) / 2.0f;
        
        x1 = (x1 - pad_x) / scale;
        y1 = (y1 - pad_y) / scale;
        x2 = (x2 - pad_x) / scale;
        y2 = (y2 - pad_y) / scale;
        
        // Clamp to image bounds
        x1 = std::max(0.0f, std::min(static_cast<float>(orig_width), x1));
        y1 = std::max(0.0f, std::min(static_cast<float>(orig_height), y1));
        x2 = std::max(0.0f, std::min(static_cast<float>(orig_width), x2));
        y2 = std::max(0.0f, std::min(static_cast<float>(orig_height), y2));
        
        Detection det;
        det.x1 = x1;
        det.y1 = y1;
        det.x2 = x2;
        det.y2 = y2;
        det.confidence = max_conf;
        det.class_id = best_class;
        det.class_name = get_class_name(best_class);
        
        candidates.push_back(det);
    }}
    
    // Apply NMS
    detections = apply_nms(candidates, iou_threshold_);
    
    // Limit to max_detections
    if (detections.size() > {self.config.postprocess.max_detections}) {{
        detections.resize({self.config.postprocess.max_detections});
    }}
    
    return detections;
}}

std::vector<Detection> Detector::apply_nms(const std::vector<Detection>& candidates,
                                           float iou_threshold) {{
    if (candidates.empty()) {{
        return {{}};
    }}
    
    // Sort by confidence (descending)
    std::vector<Detection> sorted = candidates;
    std::sort(sorted.begin(), sorted.end(),
              [](const Detection& a, const Detection& b) {{
                  return a.confidence > b.confidence;
              }});
    
    std::vector<Detection> result;
    std::vector<bool> suppressed(sorted.size(), false);
    
    for (size_t i = 0; i < sorted.size(); ++i) {{
        if (suppressed[i]) continue;
        
        result.push_back(sorted[i]);
        
        for (size_t j = i + 1; j < sorted.size(); ++j) {{
            if (suppressed[j]) continue;
            if (sorted[i].class_id != sorted[j].class_id) continue;
            
            float iou = calculate_iou(sorted[i], sorted[j]);
            if (iou > iou_threshold) {{
                suppressed[j] = true;
            }}
        }}
    }}
    
    return result;
}}

std::string Detector::get_class_name(int class_id) const {{
    if (class_id >= 0 && class_id < static_cast<int>(class_names_.size())) {{
        return class_names_[class_id];
    }}
    return "class_" + std::to_string(class_id);
}}

float Detector::calculate_iou(const Detection& a, const Detection& b) {{
    float x1 = std::max(a.x1, b.x1);
    float y1 = std::max(a.y1, b.y1);
    float x2 = std::min(a.x2, b.x2);
    float y2 = std::min(a.y2, b.y2);
    
    float inter = std::max(0.0f, x2 - x1) * std::max(0.0f, y2 - y1);
    float area_a = (a.x2 - a.x1) * (a.y2 - a.y1);
    float area_b = (b.x2 - b.x1) * (b.y2 - b.y1);
    float union_area = area_a + area_b - inter;
    
    return union_area > 0 ? inter / union_area : 0.0f;
}}

std::vector<Detection> Detector::detect(const std::string& image_path) {{
    cv::Mat image = cv::imread(image_path);
    if (image.empty()) {{
        throw std::runtime_error("Failed to load image: " + image_path);
    }}
    
    // Preprocess
    auto input_data = preprocess(image);
    
    // Create input tensor
    std::vector<int64_t> input_shape = {{1, 3, input_height_, input_width_}};
    Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(
        OrtArenaAllocator, OrtMemTypeDefault);
    
    Ort::Value input_tensor = Ort::Value::CreateTensor<float>(
        memory_info, input_data.data(), input_data.size(),
        input_shape.data(), input_shape.size());
    
    // Run inference
    const char* input_names[] = {{"{input_name}"}};
    const char* output_names[] = {{"{output_name}"}};
    
    auto outputs = session_->Run(Ort::RunOptions{{nullptr}},
                                  input_names, &input_tensor, 1,
                                  output_names, 1);
    
    // Get output
    float* output_data = outputs[0].GetTensorMutableData<float>();
    auto output_shape = outputs[0].GetTensorTypeAndShapeInfo().GetShape();
    
    size_t output_size = 1;
    for (auto dim : output_shape) {{
        output_size *= dim;
    }}
    
    std::vector<float> output(output_data, output_data + output_size);
    
    // Postprocess
    return postprocess(output, image.cols, image.rows);
}}

}} // namespace detector
"""
    
    def _render_verify_single(self, mode: ImageInputMode) -> str:
        """Render verify_single.cpp template."""
        return """#include "detector.hpp"
#include <iostream>
#include <fstream>
#include <sstream>
#include <opencv2/opencv.hpp>
#include <iomanip>

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <model.onnx> <image.jpg>" << std::endl;
        return 1;
    }
    
    std::string model_path = argv[1];
    std::string image_path = argv[2];
    
    try {
        detector::Detector detector(model_path);
        auto detections = detector.detect(image_path);
        
        std::cout << "Found " << detections.size() << " detections:" << std::endl;
        for (const auto& det : detections) {
            std::cout << "  " << det.class_name << " " << std::fixed << std::setprecision(2) << det.confidence 
                      << " [" << static_cast<int>(det.x1) << ", " << static_cast<int>(det.y1) 
                      << ", " << static_cast<int>(det.x2) << ", " << static_cast<int>(det.y2) << "]" << std::endl;
        }
        
        // Load image and draw boxes
        cv::Mat image = cv::imread(image_path);
        if (image.empty()) {
            std::cerr << "Failed to load image: " << image_path << std::endl;
            return 1;
        }
        
        int orig_w = image.cols;
        int orig_h = image.rows;
        
        for (const auto& det : detections) {
            // Draw rectangle
            cv::rectangle(image, 
                         cv::Point(static_cast<int>(det.x1), static_cast<int>(det.y1)),
                         cv::Point(static_cast<int>(det.x2), static_cast<int>(det.y2)),
                         cv::Scalar(0, 255, 0), 2);
            
            // Draw label
            std::stringstream ss;
            ss << det.class_name << " " << std::fixed << std::setprecision(2) << det.confidence;
            std::string label = ss.str();
            int baseline = 0;
            cv::Size text_size = cv::getTextSize(label, cv::FONT_HERSHEY_SIMPLEX, 0.5, 1, &baseline);
            cv::rectangle(image,
                         cv::Point(static_cast<int>(det.x1), static_cast<int>(det.y1) - text_size.height - 5),
                         cv::Point(static_cast<int>(det.x1) + text_size.width, static_cast<int>(det.y1)),
                         cv::Scalar(0, 255, 0), -1);
            cv::putText(image, label,
                       cv::Point(static_cast<int>(det.x1), static_cast<int>(det.y1) - 5),
                       cv::FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(0, 0, 0), 1);
        }
        
        // Save output image
        std::string output_path = image_path;
        size_t dot_pos = output_path.find_last_of('.');
        if (dot_pos != std::string::npos) {
            output_path = output_path.substr(0, dot_pos) + "_result.jpg";
        } else {
            output_path += "_result.jpg";
        }
        
        cv::imwrite(output_path, image);
        std::cout << "Result image saved to: " << output_path << std::endl;
        
        // Save YOLO format text file
        std::string txt_path = output_path;
        size_t txt_dot = txt_path.find_last_of('.');
        if (txt_dot != std::string::npos) {
            txt_path = txt_path.substr(0, txt_dot) + ".txt";
        } else {
            txt_path += ".txt";
        }
        
        std::ofstream txt_file(txt_path);
        for (const auto& det : detections) {
            // YOLO format: class_id x_center y_center width height confidence
            float x_center = ((det.x1 + det.x2) / 2.0f) / orig_w;
            float y_center = ((det.y1 + det.y2) / 2.0f) / orig_h;
            float width = (det.x2 - det.x1) / orig_w;
            float height = (det.y2 - det.y1) / orig_h;
            
            txt_file << det.class_id << " " 
                     << std::fixed << std::setprecision(6)
                     << x_center << " " << y_center << " "
                     << width << " " << height << " "
                     << det.confidence << std::endl;
        }
        txt_file.close();
        std::cout << "YOLO format results saved to: " << txt_path << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
"""
    
    def _render_cmake(self, mode: ImageInputMode) -> str:
        """Render CMakeLists.txt template."""
        return """cmake_minimum_required(VERSION 3.18)
project(ONNXDetector)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find packages
find_package(OpenCV REQUIRED)
find_package(onnxruntime REQUIRED)

# If onnxruntime not found, try pkg-config
if(NOT onnxruntime_FOUND)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(ONNXRUNTIME REQUIRED onnxruntime)
endif()

# Include directories
include_directories(${OpenCV_INCLUDE_DIRS})
include_directories(${ONNXRUNTIME_INCLUDE_DIRS})

# Build detector library
add_library(detector STATIC
    detector.cpp
)

target_link_libraries(detector
    ${OpenCV_LIBS}
    onnxruntime::onnxruntime
)

# Build verify_single executable
add_executable(verify_single
    verify_single.cpp
)

target_link_libraries(verify_single
    detector
    ${OpenCV_LIBS}
    onnxruntime::onnxruntime
)

# Install
install(TARGETS verify_single DESTINATION bin)
"""
    
    def _render_class_names(self) -> str:
        """Render class names array for C++."""
        if self.class_names:
            # Use provided class names
            names = [f'        "{name}"' for name in self.class_names]
            return ",\n".join(names)
        else:
            # Default COCO classes
            coco_classes = [
                "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
                "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
                "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
                "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
                "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
                "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
                "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
                "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
                "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
                "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
                "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
                "toothbrush"
            ]
            names = [f'        "{name}"' for name in coco_classes]
            return ",\n".join(names)
    
    def _render_readme(self, mode: ImageInputMode) -> str:
        """Render README.md template."""
        return f"""# ONNX Detector - Generated Code

This code was generated by ONNX Code Generator v4.

## Model Info

- Input: {self.config.input_name} (shape: {self.config.input_shape})
- Output: {', '.join(self.config.output_names) if self.config.output_names else 'output'}
- Architecture: {self.config.architecture}
- Input Size: {self.config.preprocess.input_width}x{self.config.preprocess.input_height}

## Build

```bash
mkdir build && cd build
cmake ..
make
```

## Usage

```bash
./verify_single <model.onnx> <image.jpg>
```

## Output

- Console: Detection results
- `<image>_result.jpg`: Image with bounding boxes drawn
- Detection format: [x1, y1, x2, y2, confidence, class_id]

## Extending

To process multiple images or video, modify `verify_single.cpp` or create new executables that use the `detector::Detector` class.
"""

