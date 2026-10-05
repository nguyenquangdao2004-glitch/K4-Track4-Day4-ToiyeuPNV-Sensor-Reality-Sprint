"""
FastAPI Server for Edge AI Multi-Camera Profiler.
Provides WebSocket telemetry, MJPEG video streaming, and REST control endpoints.
"""

import os
import time
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.profiler import SystemProfiler
from src.recommendation import RecommendationEngine

app = FastAPI(title="Edge AI Multi-Camera Profiler API", version="1.0.0")

static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

profiler = SystemProfiler()

class ConfigPayload(BaseModel):
    active_cameras: int = None
    resolution: str = None
    model_size: str = None
    target_fps: int = None

@app.get("/")
def get_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Multi-Camera Profiler Dashboard Loading...</h1>")

@app.get("/video_feed/{camera_id}")
def video_feed(camera_id: int):
    def frame_generator():
        while True:
            jpeg_bytes = profiler.get_camera_jpeg(camera_id)
            if jpeg_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n')
            time.sleep(0.04)
            
    return StreamingResponse(
        frame_generator(), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            telemetry = profiler.get_aggregated_telemetry()
            rec = RecommendationEngine.analyze(telemetry)
            payload = {
                "telemetry": telemetry,
                "recommendation": rec
            }
            await websocket.send_json(payload)
            await asyncio.sleep(0.35)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass

@app.post("/api/config")
def update_config(payload: ConfigPayload):
    if payload.active_cameras is not None:
        profiler.set_active_cameras(payload.active_cameras)
    if any([payload.resolution, payload.model_size, payload.target_fps]):
        profiler.set_config(
            resolution=payload.resolution,
            model_size=payload.model_size,
            target_fps=payload.target_fps
        )
    return {"status": "ok", "config": {
        "active_cameras": profiler.active_camera_count,
        "resolution": profiler.resolution,
        "model_size": profiler.model_size
    }}

@app.post("/api/stress_test/start")
def start_stress_test():
    profiler.run_stress_test(step_duration_sec=10)
    return {"status": "started"}

@app.post("/api/stress_test/stop")
def stop_stress_test():
    profiler.stop_stress_test()
    return {"status": "stopped"}

@app.post("/api/reset_metrics")
def reset_metrics():
    profiler.reset_metrics()
    return {"status": "reset"}

@app.get("/api/export_csv")
def export_csv():
    log_file = profiler.log_file
    if os.path.exists(log_file):
        return FileResponse(
            log_file, 
            filename="edge_ai_benchmarks.csv", 
            media_type="text/csv"
        )
    raise HTTPException(status_code=404, detail="Benchmark CSV not found")
