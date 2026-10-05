# Multi-Camera Bandwidth & Edge AI Performance Profiler 🚀
> **K4 - Track 4: Deployment & Edge AI | Lab Day 4**  
> **Repository nhóm:** `ToiyeuPNV-multi-camera-bandwidth-profiler`

---

## 📌 1. Giới thiệu đề tài
Hệ thống **Multi-Camera Bandwidth & Performance Profiler** được xây dựng để đo đạc và định lượng tác động của hiện tượng **nghẽn băng thông truyền thông & bão hòa tài nguyên tính toán (Bandwidth & Compute Saturation)** khi mở rộng số lượng camera trên các thiết bị Edge AI (như xe tự hành ADAS, Robot AMR nhà máy).

### 🎯 Câu hỏi nghiên cứu cốt lõi:
> *"Một thiết bị Edge AI có thể xử lý ổn định tối đa bao nhiêu luồng camera cùng lúc, và khi số camera tăng từ 1 lên 4 thì điểm nghẽn (bottleneck) bắt đầu xuất hiện ở đâu?"*

---

## 👥 2. Danh sách 5 thành viên & Báo cáo cá nhân (VLearn Submissions)
Chi tiết danh sách tại [TEAMMATES.md](TEAMMATES.md).

| STT | Họ và tên | MSSV | Vai trò chính trong dự án | Tệp báo cáo riêng nộp VLearn |
| :---: | :--- | :---: | :--- | :--- |
| **1** | **Nguyễn Quang Đạo** | **02394** | **Trưởng nhóm & System Architect / Pitch Lead** | [`reports/REPORT_NGUYEN_QUANG_DAO_02394.md`](reports/REPORT_NGUYEN_QUANG_DAO_02394.md) |
| **2** | **Ngô Thế Việt** | **02594** | **Streaming Ingestion & Network Bandwidth Engineer** | [`reports/REPORT_NGO_THE_VIET_02594.md`](reports/REPORT_NGO_THE_VIET_02594.md) |
| **3** | **Đinh Bảo Hưng** | **02524** | **AI Pipeline & Bounded Queue Engineer** | [`reports/REPORT_DINH_BAO_HUNG_02524.md`](reports/REPORT_DINH_BAO_HUNG_02524.md) |
| **4** | **Nguyễn Khánh Đô** | **02687** | **Performance Profiler & Telemetry Metrics Engineer** | [`reports/REPORT_NGUYEN_KHANH_DO_02687.md`](reports/REPORT_NGUYEN_KHANH_DO_02687.md) |
| **5** | **Đoàn Phương Linh** | **02382** | **Dashboard Visualizer & Benchmark Validation Lead** | [`reports/REPORT_DOAN_PHUONG_LINH_02382.md`](reports/REPORT_DOAN_PHUONG_LINH_02382.md) |

---

## 🏗️ 3. Kiến trúc hệ thống (System Architecture)

```
CAM 01 (Factory)   ──┐
CAM 02 (Traffic)   ──┼──> Bounded Queue (maxsize=2) ──> AI Detector (YOLO/Edge)
CAM 03 (Security)  ──┤         │                               │
CAM 04 (Warehouse) ──┘         ▼                               ▼
                         [Frame Dropper]                [Inference Done]
                               │                               │
                               └───────────────┬───────────────┘
                                               ▼
                                 [Performance Profiler Engine]
                                 • FPS (per-camera & aggregate)
                                 • End-to-End Latency (Avg & P95)
                                 • Drop Frame Rate (%)
                                 • CPU & GPU Load (%)
                                 • Ingress Bandwidth (Mbps)
                                               │
                                               ▼
                              ┌─────────────────────────────────┐
                              │    REAL-TIME WEB DASHBOARD      │
                              │  • Live 4-Camera Grid           │
                              │  • HUD Gauges & Status Pill     │
                              │  • Real-time Benchmark Charts   │
                              │  • Automated Recommendation     │
                              └─────────────────────────────────┘
```

---

## 📊 4. Bảng Benchmark có đối chứng (Experimental Results)

| Điều kiện | Số Camera | FPS / Camera | Latency (Avg / P95) | Drop Frame Rate | GPU Load | CPU Load | Ingress Bandwidth | Trạng thái hệ thống |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline** | **1 Cam** | **29.8** | 34 ms / 42 ms | **0.0%** | 35% | 22% | 2.9 Mbps | 🟢 **HEALTHY** |
| **Lỗi A (Tải vừa)** | **2 Cams** | **28.5** | 48 ms / 58 ms | **0.4%** | 54% | 34% | 5.8 Mbps | 🟢 **HEALTHY** |
| **Lỗi B (Bắt đầu suy giảm)** | **3 Cams** | **24.2** | 72 ms / 89 ms | **2.1%** | 76% | 48% | 8.7 Mbps | 🟡 **DEGRADED** |
| **Lỗi C (Quá tải bão hòa)** | **4 Cams** | **17.5** | 125 ms / 155 ms | **10.8%** | **95%** | 72% | 11.6 Mbps | 🔴 **OVERLOAD** |
| **Lỗi D (Nghẽn 1080p)** | **4 Cams (1080p)** | **14.2** | 148 ms / 195 ms | **18.5%** | **98%** | 86% | 24.8 Mbps | 🔴 **CRITICAL FAIL** |

> **Phân tích kết luận kỹ thuật:**  
> Khi tăng từ 1 lên 4 camera 720p, GPU chạm ngưỡng bão hòa **95%**, khiến hàng đợi AI xử lý không kịp tốc độ 30 FPS của camera $\rightarrow$ độ trễ tăng gấp 3.6 lần và **tỉ lệ rớt khung hình vọt lên 10.8%**.  
> **Quyết định triển khai tối ưu:** Cấu hình trần an toàn của thiết bị Edge này là **3 Cameras @ 720p 30 FPS** hoặc **4 Cameras @ 720p 15–20 FPS**.

---

## 🚀 5. Hướng dẫn cài đặt & Chạy Demo

### 1. Cài đặt môi trường
Yêu cầu Python 3.10+:
```bash
pip install opencv-python psutil fastapi uvicorn websockets numpy
```

### 2. Khởi tạo 4 video nguồn mô phỏng
```bash
python generate_videos.py
```

### 3. Khởi chạy hệ thống Profiler & Dashboard
```bash
python run.py
```

Truy cập Dashboard tại: [http://localhost:8000](http://localhost:8000)
* Bấm các nút **1 CAM, 2 CAMS, 3 CAMS, 4 CAMS** để quan sát sự thay đổi tài nguyên theo thời gian thực.
* Bấm **Run Stress Test** để chạy kịch bản tự động tăng tải.
* Bấm **Export CSV** để tải file dữ liệu thô phục vụ báo cáo.

---

## 📂 6. Cấu trúc thư mục dự án

```
K4-Track4-Day4/
├── .gitignore
├── README.md               # Tài liệu chi tiết của dự án
├── generate_videos.py      # Sinh 4 luồng video mô phỏng thực tế
├── run.py                  # Entrypoint khởi chạy server
├── src/
│   ├── detector.py         # AI detection workload với các mức stress
│   ├── camera_stream.py    # Pipeline đa luồng + Bounded buffer + Drop frame
│   ├── profiler.py         # Bộ thu thập 5 metrics và phân tích bottleneck
│   ├── recommendation.py   # Thuật toán đưa ra khuyến nghị cấu hình Edge
│   └── server.py           # FastAPI backend + WebSocket + Video Stream
├── static/
│   ├── index.html          # Giao diện giám sát Cyberpunk HUD
│   ├── css/style.css       # Hệ thống giao diện dark mode glassmorphism
│   └── js/app.js           # Client WebSocket và đồ thị Chart.js thời gian thực
├── videos/                 # 4 video camera mô phỏng
└── data/
    └── benchmarks.csv      # Log số liệu đo đạc chi tiết
```
