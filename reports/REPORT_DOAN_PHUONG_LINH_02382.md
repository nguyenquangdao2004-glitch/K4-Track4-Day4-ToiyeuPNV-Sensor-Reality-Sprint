# BÁO CÁO CÁ NHÂN LAB TRACK 4 - DAY 4
## ĐỀ TÀI 07: MULTI-CAMERA BANDWIDTH & EDGE AI PERFORMANCE PROFILING

* **Họ và tên:** **Đoàn Phương Linh**
* **MSSV:** **02382**
* **Nhóm thực hiện:** Nhóm ToiyeuPNV (5 thành viên)
* **Vai trò trong nhóm:** **Dashboard Visualizer & Benchmark Validation Lead**
* **Tệp danh sách nhóm:** [TEAMMATES.md](../TEAMMATES.md)
* **GitHub Repository chung:** [https://github.com/nguyenquangdao2004-glitch/K4-Track4-Day4-ToiyeuPNV-multi-camera-bandwidth-profiler](https://github.com/nguyenquangdao2004-glitch/K4-Track4-Day4-ToiyeuPNV-multi-camera-bandwidth-profiler)
* **Commit Version:** `1296c52`
* **Lệnh chạy tái hiện:** `python generate_videos.py && python run.py` (Dashboard: `http://localhost:8000`)

---

### 1. PROBLEM (BÀI TOÁN & SENSOR FAILURE CASE THỰC TẾ)
* **Nền tảng & Tính năng:** Hệ thống xe tự hành ADAS / Robot AMR giám sát nhà máy; phát hiện vật cản & người đi bộ 360° theo thời gian thực.
* **Cảm biến:** Mảng 4 camera bao quát 4 góc truyền tải hình ảnh liên tục.
* **Failure Case thực tế:** Thiếu khả năng cảnh báo trực quan cho người vận hành (Lack of Real-time Operator Awareness). Khi thiết bị Edge bị bão hòa tài nguyên và mất khung hình, người lái xe hoặc kỹ sư điều hành trung tâm không nhận biết được tình trạng suy giảm để can thiệp kịp thời.

### 2. METHOD (PHƯƠNG PHÁP & THAM CHIẾU KỸ THUẬT)
* **Nguồn tham chiếu:** Giao diện điều khiển công nghiệp Tesla Telemetry & NVIDIA Fleet Command Monitoring.
* **Trách nhiệm triển khai:** Xây dựng Dashboard Web Cyberpunk Dark Mode (`static/index.html`, `static/css/style.css`, `static/js/app.js`), tích hợp WebSocket đẩy telemetry thời gian thực và xây dựng hệ thống biểu đồ Chart.js tự động cập nhật.
* **Cấu trúc giao diện trực quan:**
  * Lưới 4 camera hiển thị video động kèm bounding box nhận diện đối tượng.
  * Thanh trạng thái thông minh 3 mức: **HEALTHY (Xanh)** ➔ **DEGRADED (Vàng)** ➔ **OVERLOAD (Đỏ cảnh báo)**.
  * Bộ 4 biểu đồ đường Chart.js thể hiện trực quan độ dốc suy giảm hiệu năng theo số lượng camera.
  * Nút bấm kích hoạt **"Run Stress Test"** tự động chuyển đổi tải từ 1 đến 4 camera.

### 3. BENCHMARK (KẾT QUẢ ĐO ĐẠC ĐỐI CHỨNG)
*Bằng chứng xác thực từ giao diện Dashboard tại `http://localhost:8000` (được lưu tại `data/dashboard_benchmark_evidence.png`):*
* **Baseline (1 Cam 720p):** Dashboard hiển thị badge **HEALTHY**, GPU 32.1%, FPS 30.0, Băng thông 2.94 Mbps.
* **Điều kiện A (2 Cams 720p):** 2 màn hình hoạt động, GPU 46.9%, Băng thông 6.03 Mbps.
* **Điều kiện B (3 Cams 720p):** 3 màn hình hoạt động, GPU 60.7%, Băng thông 8.85 Mbps.
* **Điều kiện C (4 Cams 720p):** 4 màn hình hoạt động đồng thời, GPU 73.8%, Băng thông 11.02 Mbps ➔ **DEGRADED**.
* **Điều kiện D (4 Cams 1080p):** Toàn bộ giao diện chuyển sang màu đỏ rực **OVERLOAD**, GPU chạm đỉnh **95.7%**, Băng thông đạt **23.00 Mbps**, hiển thị cảnh báo rớt **1,459 frames (5.6%)**.

### 4. FAILURE CASE (PHÂN TÍCH TÌNH HUỐNG QUA GIAO DIỆN)
* **Tình huống:** Bắt trọn khoảnh khắc hệ thống chuyển từ an toàn sang quá tải khi nâng phân giải lên 1080p ở 4 camera.
* **Phân định rõ ràng:**
  * *[Nhóm tự đo]:* Ảnh chụp màn hình `dashboard_benchmark_evidence.png` ghi lại chính xác dòng cảnh báo màu đỏ: `🚨 CRITICAL BOTTLENECK: GPU Saturation. Reduce AI Model complexity to 'nano' or downscale resolution to 720p`.
  * *[Nguồn tham khảo]:* Các hệ thống Edge chuẩn công nghiệp đều trang bị cơ chế tự chẩn đoán (Health Monitoring Dashboard) để phát hiện drop frame.
  * *[Suy luận kỹ thuật]:* Việc người điều khiển nhìn thấy cảnh báo OVERLOAD màu đỏ sẽ kích hoạt quy trình hạ tốc độ xe hoặc chuyển quyền kiểm soát thủ công.

### 5. ENGINEERING DECISION (QUYẾT ĐỊNH KỸ THUẬT)
1. **Tự động hóa Khuyến nghị (Automated Sizing Banner):** Tích hợp banner thông minh tự động gợi ý cấu hình triển khai tối ưu cho kỹ sư: Chuyển sang **4 Camera @ 720p 15 FPS** hoặc **3 Camera @ 1080p** khi phát hiện bão hòa phần cứng.
2. **Xuất báo cáo định lượng nhanh:** Cung cấp nút bấm **Export CSV** trực tiếp trên giao diện để trích xuất toàn bộ dữ liệu kiểm định phục vụ đối soát và báo cáo kỹ thuật.
