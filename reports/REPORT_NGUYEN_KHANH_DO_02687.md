# BÁO CÁO CÁ NHÂN LAB TRACK 4 - DAY 4
## ĐỀ TÀI 07: MULTI-CAMERA BANDWIDTH & EDGE AI PERFORMANCE PROFILING

* **Họ và tên:** **Nguyễn Khánh Đô**
* **MSSV:** **02687**
* **Nhóm thực hiện:** Nhóm ToiyeuPNV (5 thành viên)
* **Vai trò trong nhóm:** **Performance Profiler & Telemetry Metrics Engineer**
* **Tệp danh sách nhóm:** [TEAMMATES.md](../TEAMMATES.md)
* **GitHub Repository chung:** [https://github.com/nguyenquangdao2004-glitch/K4-Track4-Day4-ToiyeuPNV-Sensor-Reality-Sprint](https://github.com/nguyenquangdao2004-glitch/K4-Track4-Day4-ToiyeuPNV-Sensor-Reality-Sprint)
* **Commit Version:** `1296c52`
* **Lệnh chạy tái hiện:** `python generate_videos.py && python run.py` (Dashboard: `http://localhost:8000`)

---

### 1. PROBLEM (BÀI TOÁN & SENSOR FAILURE CASE THỰC TẾ)
* **Nền tảng & Tính năng:** Hệ thống xe tự hành ADAS / Robot AMR giám sát nhà máy; phát hiện vật cản & người đi bộ 360° theo thời gian thực.
* **Cảm biến:** Mảng 4 camera nạp dữ liệu liên tục vào hệ thống.
* **Failure Case thực tế:** Thiếu khả năng giám sát tài nguyên (Resource Blindness). Khi hệ thống bắt đầu quá tải và suy giảm chất lượng, nếu không có bộ đo lường định lượng theo thời gian thực thì xe/robot không thể tự phát hiện tình trạng mất khung hình và có biện pháp phòng ngừa rủi ro.

### 2. METHOD (PHƯƠNG PHÁP & THAM CHIẾU KỸ THUẬT)
* **Nguồn tham chiếu:** NVIDIA Tegrastats Monitoring Utility & Công cụ đo đạc hệ thống của Linux/Windows.
* **Trách nhiệm triển khai:** Xây dựng module Profiler thời gian thực (`src/profiler.py`) và cơ chế tự động ghi log vào file `data/benchmarks.csv`.
* **Phương pháp đo 5 chỉ số cốt lõi:**
  1. **FPS trượt:** Đếm số khung hình thực tế xuất ra trong cửa sổ thời gian trượt 1.0 giây.
  2. **End-to-End Latency:** Đo chính xác bằng `time.perf_counter()`, tính giá trị trung bình (Average) và phân vị 95 (P95 Latency) để phát hiện độ trễ đột biến (latency spikes).
  3. **Drop Frame Rate (%):** Tỷ lệ $\frac{\text{Tổng frame rớt}}{\text{Tổng frame nhận}} \times 100\%$.
  4. **CPU & GPU Load (%):** Đọc CPU qua `psutil.cpu_percent()` và GPU qua Windows 3D GPU Engine Counter (`Get-Counter`).
  5. **Ingress Bandwidth (Mbps):** Tính toán dung lượng mạng nạp vào theo từng luồng camera.

### 3. BENCHMARK (KẾT QUẢ ĐO ĐẠC ĐỐI CHỨNG)
*Dữ liệu tổng hợp từ 460 dòng log thực nghiệm trong `data/benchmarks.csv`:*
* **Baseline (1 Cam 720p):** FPS 30.0 | Latency Avg 5.6 ms (P95 9.0 ms) | CPU 19.6% | GPU 32.1% | Bandwidth 2.94 Mbps ➔ **HEALTHY**
* **Điều kiện A (2 Cams 720p):** FPS 25.7 | Latency Avg 5.7 ms (P95 8.1 ms) | CPU 25.6% | GPU 46.9% | Bandwidth 6.03 Mbps ➔ **HEALTHY**
* **Điều kiện B (3 Cams 720p):** FPS 27.7 | Latency Avg 5.8 ms (P95 8.0 ms) | CPU 33.1% | GPU 60.7% | Bandwidth 8.85 Mbps ➔ **DEGRADED**
* **Điều kiện C (4 Cams 720p):** FPS 30.0 | Latency Avg 5.7 ms (P95 7.5 ms) | CPU 42.6% | GPU 73.8% | Bandwidth 11.02 Mbps ➔ **DEGRADED**
* **Điều kiện D (4 Cams 1080p):** FPS 25.2 | Latency Avg 7.8 ms (P95 10.3 ms)| CPU 55.3% | GPU 95.7% | Bandwidth 23.00 Mbps | Drop Rate **5.6%** ➔ **OVERLOAD**

### 4. FAILURE CASE (PHÂN TÍCH HIỆN TƯỢNG BÃO HÒA PHẦN CỨNG)
* **Tình huống:** Khi tải tăng lên 4 camera 1080p, GPU chạm ngưỡng 95.7%.
* **Phân định rõ ràng:**
  * *[Nhóm tự đo]:* Bộ đo Profiler ghi nhận chính xác thời điểm GPU vượt ngưỡng 88% và chuyển trạng thái sang OVERLOAD, kéo theo tỉ lệ drop frame xuất hiện từ 0% vọt lên 5.6%.
  * *[Nguồn tham khảo]:* Tegrastats của NVIDIA cũng sử dụng ngưỡng cảnh báo GPU >85% và Memory bandwidth saturation để xác định bottleneck.
  * *[Suy luận kỹ thuật]:* Việc P95 latency tăng từ 7.5ms lên 10.3ms chứng tỏ đã xuất hiện hiện tượng giật khung hình cục bộ (frame jitter).

### 5. ENGINEERING DECISION (QUYẾT ĐỊNH KỸ THUẬT)
1. **Thiết lập Ngưỡng Cảnh Báo Sớm (Telemetry Alarm Threshold):** Khuyến nghị cài đặt ngưỡng tự động: Khi `gpu_load > 85%` hoặc `drop_rate > 2.0%` kéo dài trong 3 giây liên tiếp, hệ thống phải kích hoạt cờ cảnh báo an toàn cho hệ thống điều khiển xe.
2. **Quy chuẩn lưu trữ bằng chứng:** Duy trì cơ chế ghi log nhị phân hoặc CSV định kỳ để phục vụ công tác giám sát chẩn đoán hậu kỳ (Flight Data Recorder cho xe tự hành).
