# BÁO CÁO CÁ NHÂN LAB TRACK 4 - DAY 4
## ĐỀ TÀI 07: MULTI-CAMERA BANDWIDTH & EDGE AI PERFORMANCE PROFILING

* **Họ và tên:** **Đinh Bảo Hưng**
* **MSSV:** **02524**
* **Nhóm thực hiện:** Nhóm ToiyeuPNV (5 thành viên)
* **Vai trò trong nhóm:** **AI Pipeline & Bounded Queue Engineer**
* **Tệp danh sách nhóm:** [TEAMMATES.md](../TEAMMATES.md)
* **GitHub Repository chung:** [https://github.com/nguyenquangdao2004-glitch/K4-Track4-Day4-ToiyeuPNV-multi-camera-bandwidth-profiler](https://github.com/nguyenquangdao2004-glitch/K4-Track4-Day4-ToiyeuPNV-multi-camera-bandwidth-profiler)
* **Commit Version:** `1296c52`
* **Lệnh chạy tái hiện:** `python generate_videos.py && python run.py` (Dashboard: `http://localhost:8000`)

---

### 1. PROBLEM (BÀI TOÁN & SENSOR FAILURE CASE THỰC TẾ)
* **Nền tảng & Tính năng:** Hệ thống xe tự hành ADAS / Robot AMR giám sát nhà máy; phát hiện vật cản & người đi bộ 360° theo thời gian thực.
* **Cảm biến:** Mảng 4 camera nạp dữ liệu vào mô hình AI Object Detection.
* **Failure Case thực tế:** Hiện tượng bão hòa tính toán mô hình AI (Inference Saturation). Khi số lượng luồng camera tăng lên 4, tốc độ suy luận của GPU/NPU không bắt kịp tốc độ nạp khung hình 30 FPS của camera, gây ứ đọng hàng đợi và làm trôi độ trễ (latency drift).

### 2. METHOD (PHƯƠNG PHÁP & THAM CHIẾU KỸ THUẬT)
* **Nguồn tham chiếu:** Kiến trúc hàng đợi GStreamer `queue` và NVIDIA DeepStream `leaky queue`.
* **Trách nhiệm triển khai:** Thiết lập module mô hình AI (`src/detector.py`) với các mức tải tính toán (Nano, Small, Medium) và xây dựng cơ chế hàng đợi giới hạn (`bounded queue maxsize=2`).
* **Cơ chế chống trôi độ trễ:**
  * Nếu dùng hàng đợi không giới hạn (unbounded queue), khi AI chậm, hàng nghìn frame sẽ xếp hàng, làm độ trễ tích lũy tăng lên hàng chục giây (thảm họa cho xe ADAS).
  * Giải pháp Bounded Queue: Giới hạn tối đa 2 frame trong bộ đệm. Nếu frame mới đến mà hàng đợi đã đầy, hàm `put_nowait()` sẽ kích hoạt ngoại lệ `queue.Full` để hủy bỏ frame (drop frame) ngay lập tức, giữ cho độ trễ End-to-End luôn ở mức thấp nhất.

### 3. BENCHMARK (KẾT QUẢ ĐO ĐẠC ĐỐI CHỨNG)
*Số liệu đo lường hiệu năng AI và hàng đợi trích từ `data/benchmark_summary.csv`:*
* **1 Cam 720p:** FPS 30.0 | Latency 5.6 ms | Drop Rate **0.0%** | GPU 32.1% ➔ **HEALTHY**
* **2 Cams 720p:** FPS 25.7 | Latency 5.7 ms | Drop Rate **0.0%** | GPU 46.9% ➔ **HEALTHY**
* **3 Cams 720p:** FPS 27.7 | Latency 5.8 ms | Drop Rate **0.0%** | GPU 60.7% ➔ **DEGRADED**
* **4 Cams 720p:** FPS 30.0 | Latency 5.7 ms | Drop Rate **0.0%** | GPU 73.8% ➔ **DEGRADED**
* **4 Cams 1080p:** FPS 25.2 | Latency 7.8 ms (P95 10.3 ms) | Drop Rate **5.6%** | GPU **95.7%** ➔ **OVERLOAD**

### 4. FAILURE CASE (PHÂN TÍCH TÌNH HUỐNG NGHẼN AI PIPELINE)
* **Tình huống:** 4 camera 1080p @ 30 FPS khiến khối lượng tính toán ma trận tensor vượt quá công suất tính toán của GPU.
* **Phân định rõ ràng:**
  * *[Nhóm tự đo]:* GPU chạm trần 95.7%, hàng đợi `maxsize=2` bị đầy liên tục và làm hủy bỏ 1,459 frames (tỉ lệ drop 5.6%).
  * *[Nguồn tham khảo]:* NVIDIA DeepStream chỉ ra rằng khi model không xử lý kịp framerate đầu vào, cơ chế leaky buffer phải bỏ frame để ưu tiên frame mới nhất phục vụ an toàn xe.
  * *[Suy luận kỹ thuật]:* Việc drop 5.6% frame sẽ khiến thuật toán Kalman Filter/DeepSORT trên xe bị mất dấu đối tượng tạm thời trong 1–2 nhịp xử lý.

### 5. ENGINEERING DECISION (QUYẾT ĐỊNH KỸ THUẬT)
1. **Lượng tử hóa mô hình (Model Quantization):** Khuyến nghị lượng tử hóa mô hình sang định dạng **INT8 TensorRT** để tăng throughput suy luận lên 2.5–3 lần trên thiết bị Edge, giúp GPU chạy được 4 camera 1080p mà không bị quá tải.
2. **Batch Inference Optimization:** Áp dụng gom cụm batching (batch size = 4) qua plugin `nvstreammux` để tận dụng tối đa kiến trúc xử lý song song của GPU.
