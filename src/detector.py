"""
Object Detection Workload Module.
Provides AI detection with configurable workload stress (Nano, Small, Medium)
simulating real Edge AI inference (e.g. YOLO / MobileNet SSD / TensorRT).
"""

import cv2
import numpy as np
import time

class EdgeAIDetector:
    def __init__(self, model_size="nano"):
        self.model_size = model_size
        self.classes = ["person", "car", "truck", "forklift", "box", "bicycle", "helmet"]
        self.colors = [
            (0, 255, 128),  # Green
            (0, 180, 255),  # Orange
            (255, 100, 100),# Blue
            (255, 200, 0),  # Cyan
            (180, 100, 255),# Purple
            (100, 255, 255) # Yellow
        ]
        
    def set_model_size(self, model_size):
        self.model_size = model_size

    def detect(self, frame):
        t_start = time.perf_counter()
        h, w = frame.shape[:2]
        
        # Real tensor workload scaling with model_size
        if self.model_size == "nano":
            iterations = 1
            matrix_size = 400
        elif self.model_size == "small":
            iterations = 3
            matrix_size = 650
        else: # medium
            iterations = 7
            matrix_size = 850
            
        for _ in range(iterations):
            a = np.ones((matrix_size, matrix_size), dtype=np.float32) * 0.05
            _ = np.dot(a, a)
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 150)
        
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 1500 < area < 90000:
                x, y, cw, ch = cv2.boundingRect(cnt)
                if y > 55 and (y + ch) < (h - 40) and cw > 25 and ch > 25:
                    class_idx = (x + y) % len(self.classes)
                    conf = 0.75 + ((x * y) % 24) / 100.0
                    detections.append((x, y, cw, ch, self.classes[class_idx], conf, class_idx))
                    if len(detections) >= 6:
                        break
                        
        annotated_frame = frame.copy()
        for (x, y, cw, ch, cls_name, conf, c_idx) in detections:
            color = self.colors[c_idx % len(self.colors)]
            cv2.rectangle(annotated_frame, (x, y), (x + cw, y + ch), color, 2)
            label = f"{cls_name} {conf:.2f}"
            (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated_frame, (x, max(0, y - 20)), (x + lw + 6, max(20, y)), color, -1)
            cv2.putText(annotated_frame, label, (x + 3, max(15, y - 5)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            
        inference_time_ms = (time.perf_counter() - t_start) * 1000.0
        return annotated_frame, inference_time_ms, len(detections)
