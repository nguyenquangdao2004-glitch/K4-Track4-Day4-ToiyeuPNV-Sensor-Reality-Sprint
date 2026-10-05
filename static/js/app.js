document.addEventListener("DOMContentLoaded", () => {
  const statusPill = document.getElementById("system-status");
  const statusText = document.getElementById("status-text");

  const metricBw = document.getElementById("metric-bandwidth");
  const metricBwSub = document.getElementById("metric-bw-sub");
  const metricLat = document.getElementById("metric-latency");
  const metricLatSub = document.getElementById("metric-lat-sub");
  const metricDrop = document.getElementById("metric-drop");
  const metricDropSub = document.getElementById("metric-drop-sub");
  const metricCpu = document.getElementById("metric-cpu");
  const metricCpuSub = document.getElementById("metric-cpu-sub");
  const metricGpu = document.getElementById("metric-gpu");
  const metricGpuSub = document.getElementById("metric-gpu-sub");

  const recBox = document.getElementById("recommendation-box");
  const recTitle = document.getElementById("rec-title");
  const recDesc = document.getElementById("rec-desc");
  const recTag = document.getElementById("rec-tag");
  const recIcon = document.getElementById("rec-icon");

  const camButtons = document.querySelectorAll("#camera-selector .btn-toggle");
  const resSelect = document.getElementById("resolution-select");
  const modelSelect = document.getElementById("model-select");
  const btnStress = document.getElementById("btn-stress-test");
  const stressText = document.getElementById("stress-btn-text");
  const btnReset = document.getElementById("btn-reset");

  let currentActiveCams = 1;
  let isStressTesting = false;

  const benchmarkProfile = {
    1: { fps: 29.8, latAvg: 34.0, latP95: 42.0, cpu: 22.0, gpu: 35.0, bw: 2.9 },
    2: { fps: 28.5, latAvg: 48.0, latP95: 58.0, cpu: 34.0, gpu: 54.0, bw: 5.8 },
    3: { fps: 24.2, latAvg: 72.0, latP95: 89.0, cpu: 48.0, gpu: 76.0, bw: 8.7 },
    4: { fps: 17.5, latAvg: 125.0, latP95: 155.0, cpu: 72.0, gpu: 95.0, bw: 11.6 }
  };

  Chart.defaults.color = "#9ca3af";
  Chart.defaults.font.family = "'JetBrains Mono', monospace";

  const chartFps = new Chart(document.getElementById("chart-fps"), {
    type: "bar",
    data: {
      labels: ["1 Cam", "2 Cams", "3 Cams", "4 Cams"],
      datasets: [{
        label: "Avg FPS / Camera",
        data: [29.8, 28.5, 24.2, 17.5],
        backgroundColor: ["#10b981", "#10b981", "#f59e0b", "#ef4444"],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { min: 0, max: 35, grid: { color: "rgba(255,255,255,0.06)" } },
        x: { grid: { display: false } }
      },
      plugins: { legend: { display: false } }
    }
  });

  const chartLatency = new Chart(document.getElementById("chart-latency"), {
    type: "line",
    data: {
      labels: ["1 Cam", "2 Cams", "3 Cams", "4 Cams"],
      datasets: [
        {
          label: "Avg Latency (ms)",
          data: [34, 48, 72, 125],
          borderColor: "#4facfe",
          backgroundColor: "rgba(79, 172, 254, 0.15)",
          fill: true,
          tension: 0.3
        },
        {
          label: "P95 Latency (ms)",
          data: [42, 58, 89, 155],
          borderColor: "#ef4444",
          borderDash: [5, 5],
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { min: 0, max: 200, grid: { color: "rgba(255,255,255,0.06)" } },
        x: { grid: { display: false } }
      }
    }
  });

  const chartHardware = new Chart(document.getElementById("chart-hardware"), {
    type: "line",
    data: {
      labels: ["1 Cam", "2 Cams", "3 Cams", "4 Cams"],
      datasets: [
        {
          label: "GPU Compute %",
          data: [35, 54, 76, 95],
          borderColor: "#8b5cf6",
          backgroundColor: "rgba(139, 92, 246, 0.15)",
          fill: true,
          tension: 0.3
        },
        {
          label: "CPU Load %",
          data: [22, 34, 48, 72],
          borderColor: "#f59e0b",
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { min: 0, max: 100, grid: { color: "rgba(255,255,255,0.06)" } },
        x: { grid: { display: false } }
      }
    }
  });

  const chartBandwidth = new Chart(document.getElementById("chart-bandwidth"), {
    type: "line",
    data: {
      labels: ["1 Cam", "2 Cams", "3 Cams", "4 Cams"],
      datasets: [{
        label: "Ingress Mbps",
        data: [2.9, 5.8, 8.7, 11.6],
        borderColor: "#00f2fe",
        backgroundColor: "rgba(0, 242, 254, 0.15)",
        fill: true,
        tension: 0.2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { min: 0, max: 25, grid: { color: "rgba(255,255,255,0.06)" } },
        x: { grid: { display: false } }
      },
      plugins: { legend: { display: false } }
    }
  });

  let ws = null;
  function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/telemetry`;
    ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        updateDashboard(data.telemetry, data.recommendation);
      } catch (err) {
        console.error("WS Parse error:", err);
      }
    };

    ws.onclose = () => { setTimeout(connectWebSocket, 1500); };
    ws.onerror = () => { ws.close(); };
  }

  connectWebSocket();

  function updateDashboard(telem, rec) {
    if (!telem) return;

    const status = telem.status || "HEALTHY";
    statusPill.className = `system-status-pill status-${status.toLowerCase()}`;
    statusText.innerText = status;

    metricBw.innerText = telem.total_bandwidth_mbps.toFixed(1);
    metricBwSub.innerText = `${telem.active_cameras} active streams @ ${telem.resolution}`;

    metricLat.innerText = Math.round(telem.avg_latency_ms);
    metricLatSub.innerText = `P95: ${Math.round(telem.p95_latency_ms)} ms | Bottleneck: ${telem.bottleneck.split("+")[0]}`;

    metricDrop.innerText = telem.drop_rate_pct.toFixed(1);
    const totalRecv = telem.cameras.reduce((acc, c) => acc + c.total_received, 0);
    const totalDrop = telem.cameras.reduce((acc, c) => acc + c.total_dropped, 0);
    metricDropSub.innerText = `${totalDrop} dropped / ${totalRecv} total`;

    const hw = telem.hardware || {};
    metricCpu.innerText = (hw.cpu_load_pct || 0).toFixed(1);
    metricCpuSub.innerText = `RAM: ${hw.ram_load_pct || 0}% (${hw.ram_used_gb || 0} GB)`;

    metricGpu.innerText = (hw.gpu_load_pct || 0).toFixed(1);
    metricGpuSub.innerText = status === "OVERLOAD" ? "⚠️ SATURATED (Bottleneck)" : "Edge Inference Workload";

    if (rec) {
      recTitle.innerText = rec.action_item || "Operating normally";
      recDesc.innerText = rec.detailed_advice ? rec.detailed_advice.join(" ") : "";
      recTag.innerText = rec.recommended_configuration || "Maintain current config";

      if (status === "OVERLOAD") {
        recBox.style.borderLeftColor = "var(--accent-crimson)";
        recIcon.innerText = "🚨";
      } else if (status === "DEGRADED") {
        recBox.style.borderLeftColor = "var(--accent-amber)";
        recIcon.innerText = "⚠️";
      } else {
        recBox.style.borderLeftColor = "var(--accent-emerald)";
        recIcon.innerText = "💡";
      }
    }

    currentActiveCams = telem.active_cameras;
    updateActiveCameraButtons(currentActiveCams);

    for (let i = 1; i <= 4; i++) {
      const tile = document.getElementById(`cam-card-${i}`);
      const video = document.getElementById(`cam1-video`.replace("1", i));
      const offlineMsg = document.getElementById(`cam1-offline`.replace("1", i));
      const camData = telem.cameras.find((c) => c.camera_id === i);

      if (i <= currentActiveCams && camData) {
        tile.classList.remove("offline");
        if (video) video.style.display = "block";
        if (offlineMsg) offlineMsg.style.display = "none";

        document.getElementById(`cam${i}-fps`).innerText = `${camData.fps.toFixed(1)} FPS`;
        document.getElementById(`cam${i}-lat`).innerText = `${Math.round(camData.avg_latency_ms)} ms`;
        document.getElementById(`cam${i}-bw`).innerText = `${camData.bandwidth_mbps.toFixed(1)} Mbps`;
        document.getElementById(`cam${i}-drop`).innerText = `${camData.drop_rate_pct.toFixed(1)}%`;
      } else {
        tile.classList.add("offline");
        if (video) video.style.display = "none";
        if (offlineMsg) offlineMsg.style.display = "block";

        document.getElementById(`cam${i}-fps`).innerText = `-- FPS`;
        document.getElementById(`cam${i}-lat`).innerText = `-- ms`;
        document.getElementById(`cam${i}-bw`).innerText = `-- Mbps`;
        document.getElementById(`cam${i}-drop`).innerText = `0.0%`;
      }
    }

    if (currentActiveCams >= 1 && currentActiveCams <= 4) {
      const idx = currentActiveCams - 1;
      benchmarkProfile[currentActiveCams] = {
        fps: telem.avg_fps_per_cam || benchmarkProfile[currentActiveCams].fps,
        latAvg: telem.avg_latency_ms || benchmarkProfile[currentActiveCams].latAvg,
        latP95: telem.p95_latency_ms || benchmarkProfile[currentActiveCams].latP95,
        cpu: hw.cpu_load_pct || benchmarkProfile[currentActiveCams].cpu,
        gpu: hw.gpu_load_pct || benchmarkProfile[currentActiveCams].gpu,
        bw: telem.total_bandwidth_mbps || benchmarkProfile[currentActiveCams].bw
      };

      chartFps.data.datasets[0].data[idx] = benchmarkProfile[currentActiveCams].fps;
      chartFps.update();

      chartLatency.data.datasets[0].data[idx] = benchmarkProfile[currentActiveCams].latAvg;
      chartLatency.data.datasets[1].data[idx] = benchmarkProfile[currentActiveCams].latP95;
      chartLatency.update();

      chartHardware.data.datasets[0].data[idx] = benchmarkProfile[currentActiveCams].gpu;
      chartHardware.data.datasets[1].data[idx] = benchmarkProfile[currentActiveCams].cpu;
      chartHardware.update();

      chartBandwidth.data.datasets[0].data[idx] = benchmarkProfile[currentActiveCams].bw;
      chartBandwidth.update();
    }

    if (telem.stress_test_active) {
      btnStress.classList.add("running");
      stressText.innerText = `Testing ${telem.stress_test_step} Cams...`;
      isStressTesting = true;
    } else if (isStressTesting) {
      btnStress.classList.remove("running");
      stressText.innerText = "Run Stress Test";
      isStressTesting = false;
    }
  }

  function updateActiveCameraButtons(count) {
    camButtons.forEach((btn) => {
      const num = parseInt(btn.dataset.cams, 10);
      if (num === count) btn.classList.add("active");
      else btn.classList.remove("active");
    });
  }

  camButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const cams = parseInt(btn.dataset.cams, 10);
      fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ active_cameras: cams })
      });
    });
  });

  resSelect.addEventListener("change", (e) => {
    fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resolution: e.target.value })
    });
  });

  modelSelect.addEventListener("change", (e) => {
    fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_size: e.target.value })
    });
  });

  btnStress.addEventListener("click", () => {
    if (isStressTesting) fetch("/api/stress_test/stop", { method: "POST" });
    else fetch("/api/stress_test/start", { method: "POST" });
  });

  btnReset.addEventListener("click", () => {
    fetch("/api/reset_metrics", { method: "POST" });
  });
});
