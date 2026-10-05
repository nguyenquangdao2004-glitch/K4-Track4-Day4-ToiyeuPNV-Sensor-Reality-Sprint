# BÁO CÁO KẾT QUẢ THỰC NGHIỆM LAB TRACK 4 - DAY 4
## ĐỀ TÀI 07: MULTI-CAMERA BANDWIDTH & EDGE AI PERFORMANCE PROFILING

* **Nhóm thực hiện:** Nhóm 5 thành viên (ToiyeuPNV)
* **Họ và tên thành viên nộp bài:** [Điền Tên Thành Viên]
* **Vai trò trong nhóm:** [Trưởng nhóm / Streaming / AI Pipeline / Metrics Profiler / Dashboard Lead]
* **Link Repository GitHub chung:** [https://github.com/nguyenquangdao2004-glitch/K4-Track4-Day4-ToiyeuPNV-multi-camera-bandwidth-profiler](https://github.com/nguyenquangdao2004-glitch/K4-Track4-Day4-ToiyeuPNV-multi-camera-bandwidth-profiler)
* **Commit Version thẩm định:** `60202a1`
* **Lệnh chạy tái hiện:** `python generate_videos.py` && `python run.py` (Dashboard: `http://localhost:8000`)

---

### 1. PROBLEM (BÀI TOÁN & SENSOR FAILURE THỰC TẾ)
* **Nền tảng & Tính năng:** Hệ thống xe tự hành ADAS / Robot di động AMR trong nhà máy thông minh; tính năng giám sát 360° phát hiện vật cản & người đi bộ (Obstacle & Pedestrian Detection) theo thời gian thực.
* **Cảm biến:** Mảng đa camera (4 camera CSI/RTSP nạp video đồng thời).
* **Failure case thực tế:** Hiện tượng **Nghẽn băng thông truyền thông & Bão hòa tính toán (Bandwidth & Compute Saturation)** khi mở rộng số lượng camera từ 1 lên 4 stream, gây tràn bộ đệm I/O (buffer overflow), rớt khung hình (drop frame) và độ trễ tăng vọt khiến hệ thống xe/robot mất dấu đối tượng nguy hiểm.

---

### 2. METHOD (PHƯƠNG PHÁP & THAM CHIẾU KỸ THUẬT)
* **Nguồn tham chiếu:** NVIDIA DeepStream SDK Multi-Stream Performance Guide ([Link NVIDIA Docs](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Performance.html)) & Kiến trúc Bounded Queue của GStreamer.
* **Input $\rightarrow$ Output:**
  * *Input:* 4 luồng video H.264 (720p/1080p @ 30 FPS).
  * *Output:* Tọa độ bounding box nhận diện vật thể thời gian thực, bảng telemetry 5 chỉ số (FPS, Latency Avg/P95, Drop %, CPU/GPU Load, Ingress Mbps).
* **Cơ chế tái hiện trong lab:** Sử dụng Pipeline đa luồng (Multi-threaded Ingestion) với hàng đợi có giới hạn (`bounded queue maxsize=2`). Khi AI xử lý không kịp tốc độ nạp 30 FPS của camera, frame mới tự động bị loại bỏ (non-blocking drop frame) để bảo toàn độ trễ thực tế.

---

### 3. BENCHMARK (KẾT QUẢ ĐO ĐẠC ĐỐI CHỨNG CỦA NHÓM)
*Dữ liệu thực đo trích xuất từ file log `data/benchmark_summary.csv` chạy trên hệ thống:*

| Điều kiện thử nghiệm | Số Cams | Độ phân giải | FPS / Cam | Latency (Avg) | Latency (P95) | Drop Rate | CPU Load | GPU Load | Băng thông Ingress | Trạng thái |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline** | **1 Cam** | 720p | **30.0** | 5.6 ms | 9.0 ms | **0.0%** | 19.6% | 32.1% | **2.94 Mbps** | 🟢 HEALTHY |
| **Điều kiện A** | **2 Cams** | 720p | **25.7** | 5.7 ms | 8.1 ms | **0.0%** | 25.6% | 46.9% | **6.03 Mbps** | 🟢 HEALTHY |
| **Điều kiện B** | **3 Cams** | 720p | **27.7** | 5.8 ms | 8.0 ms | **0.0%** | 33.1% | 60.7% | **8.85 Mbps** | 🟡 DEGRADED |
| **Điều kiện C** | **4 Cams** | 720p | **30.0** | 5.7 ms | 7.5 ms | **0.0%** | 42.6% | **73.8%** | **11.02 Mbps** | 🟡 DEGRADED |
| **Điều kiện D (Stress)** | **4 Cams** | **1080p** | **25.2** | **7.8 ms** | **10.3 ms** | **5.6%** | **55.3%** | **95.7%** | **23.00 Mbps** | 🔴 OVERLOAD |

* **Ước lượng Băng thông thô:**
  $$\text{Raw Bandwidth (4 cams 1080p RGB24)} = 4 \times 1920 \times 1080 \times 30 \times 24\text{ bps} \approx 5.97\text{ Gbps}$$
  Cho thấy việc nén H.264 (23 Mbps) là bắt buộc vì vượt quá trần băng thông của chuẩn USB 3.0 (3.2 Gbps) và GigE (1 Gbps).

---

### 4. FAILURE CASE (PHÂN TÍCH HIỆN TƯỢNG NGHẼN CỤ THỂ)
* **Tình huống phân tích:** 4 Cameras chạy đồng thời ở độ phân giải 1080p @ 30 FPS.
* **Số liệu thực đo:** GPU chạm đỉnh bão hòa **95.7%**, CPU giải mã đạt **55.3%**, Ingress Bandwidth tăng lên **23.00 Mbps**, hàng đợi bị tràn dẫn đến **1,459 frames bị hủy (Drop rate 5.6%)**.
* **Phân định rõ ràng:**
  * *Nhóm quan sát được (Thực đo):* GPU bão hòa trên 95% là nguyên nhân trực tiếp gây nghẽn khiến hàng đợi tràn và rớt 5.6% frame.
  * *Nguồn NVIDIA DeepStream cho biết:* Khi vượt công suất giải mã/tính toán, cơ chế leaky buffer phải loại bỏ frame cũ để tránh tích lũy trễ hàng giây.
  * *Suy luận kỹ thuật (Chưa đo mAP):* Mất 5.6% frame liên tiếp khiến thuật toán bám vết bị gián đoạn, làm chậm phản ứng phanh khẩn cấp của xe thêm 0.5–1.5m.

---

### 5. ENGINEERING DECISION (QUYẾT ĐỊNH KỸ THUẬT & KHUYẾN NGHỊ TRIỂN KHAI)
1. **Xác định giới hạn thiết bị (Capacity Ceiling):** Cấu hình an toàn tối đa cho thiết bị Edge thử nghiệm là **4 Cameras @ 720p 30 FPS** (GPU 73.8%, Drop 0.0%) hoặc **3 Cameras @ 1080p**.
2. **Cải tiến kiến trúc (Adaptive Load Shedding):** Khi `gpu_load_pct > 85%`, hệ thống tự động hạ 3 camera phụ xuống **720p @ 15 FPS**, giữ nguyên camera trước 1080p @ 30 FPS để đưa GPU về dưới 75% và triệt tiêu hoàn toàn drop frame.
3. **Khuyến nghị chuẩn phần cứng:** Sử dụng giao tiếp **GMSL2 / FPD-Link III (3–6 Gbps/link)** cho xe tự hành ADAS thay cho USB/GigE thông thường để đảm bảo đồng bộ phần cứng và độ trễ thấp nhất.
