"""
Video Generator for Multi-Camera Edge AI Profiler.
Generates 4 distinct synthetic video feeds simulating realistic edge camera environments:
- CAM 1: Factory Assembly Line
- CAM 2: Smart Traffic Intersection
- CAM 3: Perimeter Security Monitor
- CAM 4: Automated Warehouse Logistics
"""

import cv2
import numpy as np
import os
import math
import time

def create_synthetic_videos(output_dir="videos", width=1280, height=720, fps=30, duration_sec=15):
    os.makedirs(output_dir, exist_ok=True)
    num_frames = fps * duration_sec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    configs = [
        {"name": "cam1.mp4", "title": "CAM 01: FACTORY ASSEMBLY LINE", "theme": "factory"},
        {"name": "cam2.mp4", "title": "CAM 02: TRAFFIC INTERSECTION", "theme": "traffic"},
        {"name": "cam3.mp4", "title": "CAM 03: PERIMETER SECURITY", "theme": "security"},
        {"name": "cam4.mp4", "title": "CAM 04: WAREHOUSE LOGISTICS", "theme": "warehouse"}
    ]
    
    print(f"Generating 4 synthetic videos ({width}x{height} @ {fps}fps, {duration_sec}s)...")
    
    for cfg in configs:
        file_path = os.path.join(output_dir, cfg["name"])
        out = cv2.VideoWriter(file_path, fourcc, fps, (width, height))
        theme = cfg["theme"]
        title = cfg["title"]
        
        for f in range(num_frames):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            t = f / fps
            
            if theme == "factory":
                frame[:] = (35, 30, 25)
                cv2.rectangle(frame, (100, 350), (1180, 500), (60, 60, 60), -1)
                cv2.line(frame, (100, 350), (1180, 350), (0, 200, 255), 2)
                cv2.line(frame, (100, 500), (1180, 500), (0, 200, 255), 2)
                
                for i in range(4):
                    part_x = int((f * 8 + i * 280) % 1000) + 120
                    cv2.rectangle(frame, (part_x, 380), (part_x + 90, 470), (50, 180, 80), -1)
                    cv2.rectangle(frame, (part_x, 380), (part_x + 90, 470), (100, 255, 120), 2)
                    cv2.putText(frame, "PART #A" + str(i+1), (part_x, 370), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 120), 1)
                
                arm_angle = math.sin(t * 3) * 0.4
                base_x, base_y = 640, 200
                arm_len = 160
                end_x = int(base_x + arm_len * math.sin(arm_angle))
                end_y = int(base_y + arm_len * math.cos(arm_angle))
                cv2.circle(frame, (base_x, base_y), 20, (180, 120, 50), -1)
                cv2.line(frame, (base_x, base_y), (end_x, end_y), (220, 150, 70), 8)
                cv2.circle(frame, (end_x, end_y), 15, (0, 220, 255), -1)
                
                w1_x = int(250 + math.sin(t * 0.8) * 40)
                cv2.rectangle(frame, (w1_x, 220), (w1_x + 70, 340), (200, 100, 30), -1)
                cv2.putText(frame, "WORKER 1", (w1_x - 10, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                
            elif theme == "traffic":
                frame[:] = (40, 40, 40)
                cv2.rectangle(frame, (200, 0), (1080, height), (30, 30, 30), -1)
                for y in range(0, height, 80):
                    y_offset = int((y + f * 10) % height)
                    cv2.line(frame, (640, y_offset), (640, y_offset + 40), (255, 255, 255), 4)
                
                car1_y = int((f * 14) % (height + 150)) - 100
                cv2.rectangle(frame, (450, car1_y), (550, car1_y + 130), (220, 50, 50), -1)
                cv2.rectangle(frame, (450, car1_y), (550, car1_y + 130), (255, 100, 100), 2)
                cv2.putText(frame, "SEDAN [54 km/h]", (440, car1_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 100), 1)
                
                car2_y = height - int((f * 18) % (height + 180)) + 50
                cv2.rectangle(frame, (730, car2_y), (850, car2_y + 160), (40, 140, 230), -1)
                cv2.rectangle(frame, (730, car2_y), (850, car2_y + 160), (80, 180, 255), 2)
                cv2.putText(frame, "TRUCK [42 km/h]", (730, car2_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 180, 255), 1)
                
            elif theme == "security":
                frame[:] = (20, 25, 20)
                for x in range(100, width - 100, 60):
                    cv2.line(frame, (x, 200), (x, 600), (50, 60, 50), 1)
                cv2.line(frame, (100, 300), (width - 100, 300), (80, 80, 80), 2)
                cv2.line(frame, (100, 500), (width - 100, 500), (80, 80, 80), 2)
                
                p1_x = int(width/2 + math.sin(t * 1.2) * 350)
                p1_y = 420
                cv2.rectangle(frame, (p1_x - 30, p1_y - 70), (p1_x + 30, p1_y + 70), (60, 160, 220), -1)
                cv2.circle(frame, (p1_x, p1_y - 90), 20, (60, 160, 220), -1)
                cv2.putText(frame, "GUARD [ID: 04]", (p1_x - 50, p1_y - 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 220, 255), 1)
                
                scan_y = int(250 + (math.sin(t * 2) + 1) * 150)
                cv2.line(frame, (150, scan_y), (1130, scan_y), (0, 0, 255), 1)
                cv2.putText(frame, "LASER PERIMETER ACTIVE", (150, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                
            elif theme == "warehouse":
                frame[:] = (28, 28, 35)
                for y in [180, 340, 500]:
                    cv2.rectangle(frame, (80, y), (1200, y + 20), (100, 100, 120), -1)
                for c_x in range(120, 1150, 140):
                    cv2.rectangle(frame, (c_x, 210), (c_x + 90, 335), (140, 100, 50), -1)
                    cv2.rectangle(frame, (c_x + 10, 370), (c_x + 80, 495), (110, 80, 40), -1)
                
                agv_x = int(200 + (t * 100) % 800)
                cv2.rectangle(frame, (agv_x, 540), (agv_x + 140, 630), (250, 160, 0), -1)
                cv2.rectangle(frame, (agv_x + 110, 510), (agv_x + 135, 540), (180, 180, 180), -1)
                cv2.putText(frame, "AGV ROBOT #02", (agv_x, 530), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            cv2.rectangle(frame, (0, 0), (width, 50), (15, 15, 15), -1)
            cv2.putText(frame, f"[LIVE] {title}", (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 200), 2)
            timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S") + f".{int((f % fps) * (1000/fps)):03d}"
            cv2.putText(frame, timestamp_str, (width - 320, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
            
            cv2.rectangle(frame, (0, height - 35), (width, height), (10, 10, 10), -1)
            cv2.putText(frame, f"Stream: RTSP://192.168.1.10{configs.index(cfg)+1}:554/live  |  Codec: H.264  |  Frame: {f:04d}", 
                        (20, height - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (140, 140, 140), 1)
            
            out.write(frame)
        out.release()
        print(f"Generated {cfg['name']} successfully.")

if __name__ == "__main__":
    create_synthetic_videos()
