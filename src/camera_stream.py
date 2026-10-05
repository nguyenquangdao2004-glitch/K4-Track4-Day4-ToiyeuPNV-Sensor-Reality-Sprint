"""
Multi-Camera Stream Ingestion & Processing Pipeline.
Simulates real-time RTSP cameras with bounded queues, backpressure drop frames,
and precise end-to-end latency tracking.
"""

import cv2
import time
import threading
import queue
import numpy as np
from src.detector import EdgeAIDetector

class CameraStream:
    def __init__(self, camera_id, video_path, target_fps=30, resolution="720p", model_size="nano"):
        self.camera_id = camera_id
        self.video_path = video_path
        self.target_fps = target_fps
        self.resolution = resolution
        self.detector = EdgeAIDetector(model_size=model_size)
        
        self.res_map = {
            "360p": (640, 360),
            "720p": (1280, 720),
            "1080p": (1920, 1080)
        }
        
        # Real-time bounded buffer (Max 2 frames; backpressure queue)
        self.frame_queue = queue.Queue(maxsize=2)
        
        self.total_received = 0
        self.total_processed = 0
        self.total_dropped = 0
        
        self.current_fps = 0.0
        self.avg_latency_ms = 0.0
        self.p95_latency_ms = 0.0
        self.inference_latency_ms = 0.0
        self.ingest_latency_ms = 0.0
        self.bandwidth_mbps = 0.0
        
        self.latency_history = []
        self.fps_timestamps = []
        self.bandwidth_samples = []
        
        self.latest_display_frame = None
        self.latest_jpeg = None
        self.lock = threading.Lock()
        
        self.running = False
        self.capture_thread = None
        self.process_thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.capture_thread.start()
        self.process_thread.start()

    def stop(self):
        self.running = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
        if self.process_thread and self.process_thread.is_alive():
            self.process_thread.join(timeout=1.0)

    def set_config(self, resolution=None, model_size=None, target_fps=None):
        if resolution and resolution in self.res_map:
            self.resolution = resolution
        if model_size:
            self.detector.set_model_size(model_size)
        if target_fps:
            self.target_fps = target_fps

    def _capture_loop(self):
        cap = cv2.VideoCapture(self.video_path)
        frame_interval = 1.0 / self.target_fps
        target_w, target_h = self.res_map.get(self.resolution, (1280, 720))
        
        while self.running:
            t_loop_start = time.perf_counter()
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
                
            if frame.shape[1] != target_w or frame.shape[0] != target_h:
                frame = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
                
            self.total_received += 1
            t_ingest = time.perf_counter()
            
            base_mbps = {"360p": 0.85, "720p": 2.9, "1080p": 6.2}.get(self.resolution, 2.9)
            jitter = (np.sin(self.total_received * 0.1) * 0.15) * base_mbps
            instant_mbps = max(0.2, base_mbps + jitter)
            self.bandwidth_samples.append(instant_mbps)
            if len(self.bandwidth_samples) > 30:
                self.bandwidth_samples.pop(0)
            self.bandwidth_mbps = float(np.mean(self.bandwidth_samples))
            
            # Enqueue frame; if buffer full, DROP FRAME
            try:
                self.frame_queue.put_nowait((frame, t_ingest))
            except queue.Full:
                self.total_dropped += 1
                
            elapsed = time.perf_counter() - t_loop_start
            sleep_time = frame_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
                
        cap.release()

    def _process_loop(self):
        while self.running:
            try:
                frame, t_ingest = self.frame_queue.get(timeout=0.2)
            except queue.Empty:
                continue
                
            t_start_process = time.perf_counter()
            ingest_latency = (t_start_process - t_ingest) * 1000.0
            
            annotated_frame, infer_time_ms, num_dets = self.detector.detect(frame)
            
            t_done = time.perf_counter()
            e2e_latency = (t_done - t_ingest) * 1000.0
            
            self.total_processed += 1
            
            now = time.perf_counter()
            self.fps_timestamps.append(now)
            self.fps_timestamps = [t for t in self.fps_timestamps if now - t <= 1.0]
            self.current_fps = float(len(self.fps_timestamps))
            
            self.inference_latency_ms = infer_time_ms
            self.ingest_latency_ms = ingest_latency
            
            self.latency_history.append(e2e_latency)
            if len(self.latency_history) > 60:
                self.latency_history.pop(0)
                
            self.avg_latency_ms = float(np.mean(self.latency_history)) if self.latency_history else 0.0
            self.p95_latency_ms = float(np.percentile(self.latency_history, 95)) if self.latency_history else 0.0
            
            h, w = annotated_frame.shape[:2]
            cv2.rectangle(annotated_frame, (10, h - 35), (320, h - 10), (0, 0, 0), -1)
            hud_text = f"FPS: {self.current_fps:.1f} | Lat: {e2e_latency:.0f}ms | Drop: {self.get_drop_rate():.1f}%"
            cv2.putText(annotated_frame, hud_text, (15, h - 18), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 200), 1, cv2.LINE_AA)
            
            preview_frame = cv2.resize(annotated_frame, (640, 360), interpolation=cv2.INTER_AREA)
            ret, jpeg = cv2.imencode('.jpg', preview_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if ret:
                with self.lock:
                    self.latest_jpeg = jpeg.tobytes()
                    self.latest_display_frame = annotated_frame
                    
            self.frame_queue.task_done()

    def get_drop_rate(self):
        if self.total_received == 0:
            return 0.0
        return (self.total_dropped / float(self.total_received)) * 100.0

    def get_jpeg(self):
        with self.lock:
            return self.latest_jpeg

    def get_telemetry(self):
        return {
            "camera_id": self.camera_id,
            "fps": round(self.current_fps, 1),
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "p95_latency_ms": round(self.p95_latency_ms, 1),
            "inference_ms": round(self.inference_latency_ms, 1),
            "ingest_ms": round(self.ingest_latency_ms, 1),
            "drop_rate_pct": round(self.get_drop_rate(), 2),
            "total_received": self.total_received,
            "total_dropped": self.total_dropped,
            "bandwidth_mbps": round(self.bandwidth_mbps, 2),
            "resolution": self.resolution
        }
