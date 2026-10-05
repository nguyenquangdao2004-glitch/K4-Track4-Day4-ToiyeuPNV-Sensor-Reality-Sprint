"""
Edge AI Deployment Sizing & Optimization Recommendation Engine.
"""

class RecommendationEngine:
    @staticmethod
    def analyze(telemetry):
        active_cams = telemetry.get("active_cameras", 1)
        res = telemetry.get("resolution", "720p")
        model = telemetry.get("model_size", "nano")
        status = telemetry.get("status", "HEALTHY")
        fps = telemetry.get("avg_fps_per_cam", 30.0)
        lat = telemetry.get("avg_latency_ms", 35.0)
        p95 = telemetry.get("p95_latency_ms", 45.0)
        drop = telemetry.get("drop_rate_pct", 0.0)
        bw = telemetry.get("total_bandwidth_mbps", 5.0)
        hw = telemetry.get("hardware", {})
        cpu = hw.get("cpu_load_pct", 25.0)
        gpu = hw.get("gpu_load_pct", 40.0)
        
        if res == "1080p":
            max_cams_nano = 3
            max_cams_small = 2
            max_cams_med = 1
        elif res == "720p":
            max_cams_nano = 4
            max_cams_small = 3
            max_cams_med = 2
        else:
            max_cams_nano = 6
            max_cams_small = 4
            max_cams_med = 3
            
        cur_max = {"nano": max_cams_nano, "small": max_cams_small, "medium": max_cams_med}.get(model, 3)
        
        advice_list = []
        action_item = ""
        
        if status == "OVERLOAD":
            if gpu > 88:
                action_item = "CRITICAL BOTTLENECK: GPU Saturation. Reduce AI Model complexity to 'nano' or downscale resolution to 720p."
                advice_list.append("GPU compute pipeline is saturated (>88%). Inference cannot keep pace with RTSP 30 FPS ingestion.")
            elif cpu > 85:
                action_item = "CRITICAL BOTTLENECK: CPU Saturation. Video decode & thread scheduling overhead exceeded host capacity."
                advice_list.append("CPU decoding is bottlenecking. Enable hardware-accelerated video decoding (NVDEC / QSV).")
            elif bw > 18:
                action_item = "CRITICAL BOTTLENECK: Bandwidth Exhaustion. Total network ingress exceeds edge link capacity (18+ Mbps)."
                advice_list.append("Use H.265 / AV1 codec or reduce camera resolution from 1080p to 720p to save ~55% bandwidth.")
            else:
                action_item = "CRITICAL BOTTLENECK: Processing Latency Accumulation. Backpressure queues are overflowing."
                advice_list.append("Frames are dropping at queue level due to mismatched ingestion vs processing velocity.")
                
            rec_config = f"Switch to {min(active_cams, cur_max)} Cameras @ 720p 15 FPS with Nano model"
            
        elif status == "DEGRADED":
            action_item = "WARNING: System nearing operational limits. Frame latency jitter observed."
            advice_list.append(f"Operating at {active_cams} streams with {p95:.0f}ms P95 latency. Headroom is less than 15%.")
            rec_config = f"Recommended to cap at {cur_max} cameras or optimize model quantization (INT8 / TensorRT)."
        else:
            action_item = "OPTIMAL: All pipeline stages within Edge SLA limits (FPS ≥ 22, Latency ≤ 70ms, Drop ≤ 2.5%)."
            advice_list.append(f"System has sufficient headroom for up to {cur_max} streams under current {res} configuration.")
            rec_config = f"Production Ready: Maintain current configuration ({active_cams} Cameras @ {res})."
            
        bw_per_cam = bw / max(1, active_cams)
        required_switch_port = "100 Mbps FastEthernet" if bw < 70 else "1 Gbps Gigabit"
        
        return {
            "status": status,
            "action_item": action_item,
            "detailed_advice": advice_list,
            "recommended_configuration": rec_config,
            "max_sustainable_cameras": cur_max,
            "estimated_bandwidth_per_cam_mbps": round(bw_per_cam, 2),
            "recommended_network_infrastructure": required_switch_port,
            "sla_compliance": {
                "fps_sla_met": fps >= 20.0,
                "latency_sla_met": lat <= 100.0,
                "drop_rate_sla_met": drop <= 5.0,
                "gpu_sla_met": gpu <= 85.0
            }
        }
