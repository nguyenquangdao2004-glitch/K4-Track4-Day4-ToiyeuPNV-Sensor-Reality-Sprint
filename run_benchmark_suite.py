"""
Automated Benchmark Suite Runner for Multi-Camera Profiling.
Executes Baseline, Condition A (2 cams), Condition B (3 cams), Condition C (4 cams 720p), and Condition D (4 cams 1080p).
Logs and computes average quantitative values for each condition.
"""

import urllib.request
import json
import time
import pandas as pd
import os

SERVER_URL = "http://127.0.0.1:8000"

def set_config(active_cams, resolution="720p", model_size="nano"):
    url = f"{SERVER_URL}/api/config"
    data = json.dumps({
        "active_cameras": active_cams,
        "resolution": resolution,
        "model_size": model_size
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def reset_metrics():
    url = f"{SERVER_URL}/api/reset_metrics"
    req = urllib.request.Request(url, data=b"{}", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def run_suite():
    print("=" * 70)
    print("STARTING AUTOMATED MULTI-CAMERA BENCHMARK SUITE")
    print("=" * 70)
    
    phases = [
        {"name": "Baseline (1 Cam, 720p)", "cams": 1, "res": "720p", "duration": 10},
        {"name": "Condition A (2 Cams, 720p)", "cams": 2, "res": "720p", "duration": 10},
        {"name": "Condition B (3 Cams, 720p)", "cams": 3, "res": "720p", "duration": 10},
        {"name": "Condition C (4 Cams, 720p)", "cams": 4, "res": "720p", "duration": 10},
        {"name": "Condition D (4 Cams, 1080p)", "cams": 4, "res": "1080p", "duration": 10}
    ]
    
    results = []
    
    for p in phases:
        print(f"\n---> Running: {p['name']} for {p['duration']} seconds...")
        set_config(p['cams'], p['res'])
        reset_metrics()
        time.sleep(2) # warmup
        
        # Monitor over duration
        time.sleep(p['duration'])
        
    print("\nBenchmark runs complete! Analyzing CSV data...")
    csv_file = "data/benchmarks.csv"
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        print(f"Total benchmark snapshots logged: {len(df)}")
        # Group by active_cameras and resolution
        summary = df.groupby(["active_cameras", "resolution"]).agg({
            "avg_fps_per_cam": "mean",
            "avg_latency_ms": "mean",
            "p95_latency_ms": "mean",
            "drop_rate_pct": "mean",
            "cpu_load_pct": "mean",
            "gpu_load_pct": "mean",
            "total_bandwidth_mbps": "mean"
        }).reset_index()
        
        print("\n" + "=" * 70)
        print("EMPIRICAL BENCHMARK SUMMARY (QUANTITATIVE RESULTS)")
        print("=" * 70)
        print(summary.to_string(index=False))
        
        # Save summary
        summary.to_csv("data/benchmark_summary.csv", index=False)
        print("\nSaved summary to data/benchmark_summary.csv")

if __name__ == "__main__":
    run_suite()
