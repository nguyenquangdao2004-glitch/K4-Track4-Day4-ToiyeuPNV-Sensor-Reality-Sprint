"""
Multi-Camera Edge AI Bandwidth Profiler
Entrypoint script to launch the FastAPI server and telemetry engine.
"""

import uvicorn
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("=" * 70)
    print("  MULTI-CAMERA BANDWIDTH & EDGE AI PERFORMANCE PROFILER")
    print("  Track 4: Deployment & Edge AI Benchmarking Suite")
    print("=" * 70)
    print("  Server starting on: http://127.0.0.1:8000")
    print("  Dashboard UI:       http://localhost:8000")
    print("  Telemetry WS:       ws://localhost:8000/ws/telemetry")
    print("=" * 70)
    
    uvicorn.run("src.server:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
