# BÁO CÁO CÁ NHÂN LAB TRACK 4 - DAY 4
## ĐỀ TÀI 07: MULTI-CAMERA BANDWIDTH & EDGE AI PERFORMANCE PROFILING

* **Họ và tên:** **Ngô Thế Việt**
* **MSSV:** **02594**
* **Nhóm thực hiện:** Nhóm ToiyeuPNV (5 thành viên)
* **Vai trò trong nhóm:** **Streaming Ingestion & Network Bandwidth Engineer**
* **Tệp danh sách nhóm:** [TEAMMATES.md](../TEAMMATES.md)
* **GitHub Repository chung:** [https://github.com/nguyenquangdao2004-glitch/K4-Track4-Day4-ToiyeuPNV-multi-camera-bandwidth-profiler](https://github.com/nguyenquangdao2004-glitch/K4-Track4-Day4-ToiyeuPNV-multi-camera-bandwidth-profiler)
* **Commit Version:** `1296c52`
* **Lệnh chạy tái hiện:** `python generate_videos.py && python run.py` (Dashboard: `http://localhost:8000`)

---

### 1. PROBLEM (BÀI TOÁN & SENSOR FAILURE CASE THỰC TẾ)
* **Nền tảng & Tính năng:** Hệ thống xe tự hành ADAS / Robot AMR nhà máy; tính năng giám sát 360° phát hiện vật cản & người đi bộ theo thời gian thực.
* **Cảm biến:** Mảng 4 camera truyền luồng video số lượng lớn về trung tâm xử lý.
* **Failure Case thực tế:** Nghẽn băng thông truyền thông (Bandwidth Bottleneck). Khi truyền tải đồng thời 4 luồng video chất lượng cao, dung lượng dữ liệu thô vượt quá năng lực truyền dẫn của bus I/O hoặc cáp mạng, dẫn đến nghẽn đường truyền và làm chậm khâu giải mã khung hình.

### 2. METHOD (PHƯƠNG PHÁP & THAM CHIẾU KỸ THUẬT)
* **Nguồn tham chiếu:** Chuẩn băng thông giao tiếp Basler Camera Documentation & NVIDIA DeepStream Multi-Stream Ingestion.
* **Trách nhiệm triển khai:** Thiết lập module nạp luồng camera đa luồng (`src/camera_stream.py`), điều chỉnh độ phân giải (360p, 720p, 1080p), ước lượng và đo đạc lưu lượng mạng thực tế (Ingress Bandwidth Mbps).
* **Công thức ước lượng băng thông thô (Raw Uncompressed Bandwidth):**
  $$\text{Raw Bandwidth} = N_{\text{cams}} \times W \times H \times \text{FPS} \times \text{bit/pixel}$$
  Với 4 camera 1080p @ 30 FPS RGB24 (24 bits/pixel):
  $$\text{Raw Bandwidth} = 4 \times 1920 \times 1080 \times 30 \times 24 = 5,971,968,000\text{ bps} \approx 5.97\text{ Gbps}$$

### 3. BENCHMARK (KẾT QUẢ ĐO ĐẠC ĐỐI CHỨNG)
*Kết quả đo băng thông thực tế (H.264 stream) trích từ `data/benchmark_summary.csv`:*
* **1 Cam 720p:** Băng thông nạp **2.94 Mbps** | FPS 30.0 | Latency 5.6 ms ➔ **HEALTHY**
* **2 Cams 720p:** Băng thông nạp **6.03 Mbps** | FPS 25.7 | Latency 5.7 ms ➔ **HEALTHY**
* **3 Cams 720p:** Băng thông nạp **8.85 Mbps** | FPS 27.7 | Latency 5.8 ms ➔ **DEGRADED**
* **4 Cams 720p:** Băng thông nạp **11.02 Mbps** | FPS 30.0 | Latency 5.7 ms ➔ **DEGRADED**
* **4 Cams 1080p:** Băng thông nạp vọt lên **23.00 Mbps** | GPU 95.7% | Drop rate **5.6%** ➔ **OVERLOAD**

### 4. FAILURE CASE (PHÂN TÍCH TÌNH HUỐNG NGHẼN BĂNG THÔNG)
* **Tình huống:** Chuyển 4 camera từ 720p sang 1080p khiến băng thông nạp tăng gấp đôi (từ 11.02 lên 23.00 Mbps).
* **Phân định rõ ràng:**
  * *[Nhóm tự đo]:* Băng thông mạng tăng tuyến tính theo số camera và độ phân giải, đạt đỉnh 23.00 Mbps tại 4 camera 1080p.
  * *[Nguồn tham khảo]:* Nếu truyền video thô (5.97 Gbps), các cổng giao tiếp USB 3.0 (trần 3.2 Gbps thực tế) và Gigabit Ethernet (trần 1 Gbps) sẽ hoàn toàn bị nghẽn tắc.
  * *[Suy luận kỹ thuật]:* Việc bắt buộc phải nén H.264 đã giúp giảm băng thông từ 5.97 Gbps xuống 23 Mbps (tiết kiệm ~260 lần), nhưng tạo ra gánh nặng giải mã đè lên CPU máy chủ (chiếm 55.3% CPU).

### 5. ENGINEERING DECISION (QUYẾT ĐỊNH KỸ THUẬT)
1. **Khuyến nghị giao tiếp vật lý:** Đề xuất sử dụng chuẩn giao tiếp **GMSL2 SerDes (3–6 Gbps/link)** hoặc **MIPI CSI-2 (4-lane)** cho các hệ thống xe tự hành ADAS để có thể truyền tải luồng video trực tiếp vào bộ nhớ DMA mà không làm nghẽn bus mạng.
2. **Cấu hình băng thông tối ưu:** Giữ độ phân giải ở mức **720p (băng thông ~2.9 Mbps/camera)** để duy trì tổng băng thông toàn hệ thống dưới 12 Mbps, đảm bảo an toàn tuyệt đối cho đường truyền mạng nội bộ của xe/robot.
