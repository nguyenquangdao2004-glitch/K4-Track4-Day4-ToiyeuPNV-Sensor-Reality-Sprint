# BÁO CÁO CÁ NHÂN LAB TRACK 4 - DAY 4
## ĐỀ TÀI 07: MULTI-CAMERA BANDWIDTH & EDGE AI PERFORMANCE PROFILING

* **Họ và tên:** **Nguyễn Quang Đạo**
* **MSSV:** **02394**
* **Nhóm thực hiện:** Nhóm ToiyeuPNV (5 thành viên)
* **Vai trò trong nhóm:** **Trưởng nhóm & System Architecture / Pitching Lead**
* **Tệp danh sách nhóm:** [TEAMMATES.md](../TEAMMATES.md)
* **GitHub Repository chung:** [https://github.com/nguyenquangdao2004-glitch/K4-Track4-Day4-ToiyeuPNV-multi-camera-bandwidth-profiler](https://github.com/nguyenquangdao2004-glitch/K4-Track4-Day4-ToiyeuPNV-multi-camera-bandwidth-profiler)
* **Commit Version:** `1296c52`
* **Lệnh chạy tái hiện:** `python generate_videos.py && python run.py` (Dashboard: `http://localhost:8000`)

---

### 1. PROBLEM (BÀI TOÁN & SENSOR FAILURE CASE THỰC TẾ)
* **Nền tảng & Tính năng:** Hệ thống xe tự hành ADAS / Robot AMR giám sát nhà máy thông minh; tính năng giám sát 360° phát hiện vật cản & người đi bộ (Obstacle & Pedestrian Detection) theo thời gian thực.
* **Cảm biến:** Mảng đa camera (4 camera CSI/RTSP bao quát 4 góc).
* **Failure Case thực tế:** Hiện tượng **Nghẽn băng thông truyền thông & Bão hòa tính toán (Bandwidth & Compute Saturation)** khi mở rộng số lượng camera từ 1 lên 4 streams. Tốc độ frame gửi tới (120 FPS tổng) vượt quá công suất giải mã CPU và suy luận GPU, gây tràn bộ đệm (buffer overflow), rớt khung hình (drop frame) và tăng độ trễ khiến xe/robot mất dấu đối tượng nguy hiểm.

### 2. METHOD (PHƯƠNG PHÁP & THAM CHIẾU KỸ THUẬT)
* **Nguồn tham chiếu:** NVIDIA DeepStream SDK Performance Guide ([Link NVIDIA Docs](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Performance.html)) và cơ chế Bounded Queue của GStreamer.
* **Input $\rightarrow$ Output:** Nhận 4 luồng video H.264 (720p/1080p @ 30 FPS) $\rightarrow$ Xuất tọa độ bounding box vật thể và bảng telemetry 5 chỉ số (FPS, Latency Avg/P95, Drop %, CPU/GPU Load, Ingress Bandwidth Mbps).
* **Cơ chế kiểm soát:** Sử dụng Pipeline đa luồng với hàng đợi có giới hạn (`bounded queue maxsize=2`). Khi AI xử lý không kịp tốc độ nạp 30 FPS của camera, frame mới tự động bị loại bỏ (non-blocking drop frame) để bảo toàn độ trễ thực tế, tránh tích lũy trễ hàng giây.

### 3. BENCHMARK (KẾT QUẢ ĐO ĐẠC ĐỐI CHỨNG)
*Số liệu trích xuất từ file log chung của nhóm `data/benchmark_summary.csv`:*
* **Baseline (1 Cam 720p):** FPS 30.0 | Latency Avg 5.6 ms (P95 9.0 ms) | Drop 0.0% | CPU 19.6% | GPU 32.1% | Bandwidth 2.94 Mbps ➔ **HEALTHY**
* **Điều kiện A (2 Cams 720p):** FPS 25.7 | Latency Avg 5.7 ms (P95 8.1 ms) | Drop 0.0% | CPU 25.6% | GPU 46.9% | Bandwidth 6.03 Mbps ➔ **HEALTHY**
* **Điều kiện B (3 Cams 720p):** FPS 27.7 | Latency Avg 5.8 ms (P95 8.0 ms) | Drop 0.0% | CPU 33.1% | GPU 60.7% | Bandwidth 8.85 Mbps ➔ **DEGRADED**
* **Điều kiện C (4 Cams 720p):** FPS 30.0 | Latency Avg 5.7 ms (P95 7.5 ms) | Drop 0.0% | CPU 42.6% | GPU 73.8% | Bandwidth 11.02 Mbps ➔ **DEGRADED**
* **Điều kiện D (4 Cams 1080p):** FPS 25.2 | Latency Avg 7.8 ms (P95 10.3 ms)| Drop 5.6% | CPU 55.3% | GPU 95.7% | Bandwidth 23.00 Mbps ➔ **OVERLOAD**

### 4. FAILURE CASE (PHÂN TÍCH TÌNH HUỐNG NGHẼN ĐIỂN HÌNH)
* **Tình huống phân tích:** 4 Cameras chạy đồng thời @ 1080p 30 FPS.
* **Số liệu thực đo:** GPU chạm đỉnh **95.7%**, CPU giải mã đạt **55.3%**, Ingress Bandwidth vọt lên **23.00 Mbps**, hàng đợi bị tràn làm **1,459 frames bị hủy (Drop rate 5.6%)**.
* **Phân định 3 cấp độ thông tin:**
  * *[Nhóm tự đo]:* GPU bão hòa trên 95% là nguyên nhân chính gây tràn hàng đợi và rớt 5.6% frame (chứng minh qua log `benchmarks.csv`).
  * *[Nguồn tham khảo]:* NVIDIA DeepStream chỉ ra rằng khi vượt công suất phần cứng, bắt buộc phải dùng leaky queue để tránh tích lũy trễ hàng giây.
  * *[Suy luận kỹ thuật]:* Rớt 5.6% frame liên tiếp làm đứt đoạn trajectory bám vết đối tượng, làm chậm phản xạ phanh ADAS thêm 0.5–1.5m.

### 5. ENGINEERING DECISION (QUYẾT ĐỊNH KỸ THUẬT & KHUYẾN NGHỊ)
1. **Xác định giới hạn thiết bị (Capacity Ceiling):** Cấu hình an toàn tối đa cho phần cứng Edge này là **4 Cameras @ 720p 30 FPS** (GPU 73.8%, Drop 0.0%) hoặc **3 Cameras @ 1080p**.
2. **Cải tiến kiến trúc (Adaptive Load Shedding):** Khi `gpu_load_pct > 85%`, hệ thống tự động hạ 3 camera phụ xuống **720p @ 15 FPS**, giữ camera trước 1080p @ 30 FPS để hạ GPU về <75% và triệt tiêu drop frame.
3. **Khuyến nghị chuẩn phần cứng:** Sử dụng giao tiếp **GMSL2 / FPD-Link III (3–6 Gbps/link)** cho xe tự hành ADAS thay cho USB 3.0 và Ethernet dân dụng.
