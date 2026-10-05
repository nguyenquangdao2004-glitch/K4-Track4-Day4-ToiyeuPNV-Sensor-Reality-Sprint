# MULTI-CAMERA BANDWIDTH & EDGE AI PERFORMANCE PROFILING
## Slide Thuyết Trình Bài Lab Track 4 - Day 4 (Thời gian: 3–5 Phút)

---

## SLIDE 1: TỔNG QUAN ĐỀ TÀI & NHÓM THỰC HIỆN
* **Đề tài:** Multi-Camera Bandwidth & Performance Profiling trên Edge AI
* **Lĩnh vực:** Deployment / Edge AI / Real-time Systems
* **Nhóm thực hiện (5 thành viên - ToiyeuPNV):**
  1. **Thành viên 1:** Trưởng nhóm & Kịch bản / Trình bày Pitching
  2. **Thành viên 2:** Streaming Ingestion & Băng thông mạng
  3. **Thành viên 3:** AI Workload & Hàng đợi Bounded Buffer
  4. **Thành viên 4:** Metrics Profiler & CSV Telemetry Engine
  5. **Thành viên 5:** Dashboard Trực quan hóa & Thử nghiệm Benchmark
* **Repository:** `https://github.com/nguyenquangdao2004-glitch/K4-Track4-Day4-ToiyeuPNV-multi-camera-bandwidth-profiler`

> **Lời thuyết minh (Speaker Note):**  
> *"Kính chào thầy cô và các bạn. Nhóm em gồm 5 thành viên chọn Đề tài 7: Multi-Camera Bandwidth Profiling. Trong các hệ thống xe tự hành ADAS hay robot nhà máy, việc kết hợp nhiều camera là bắt buộc. Trọng tâm bài lab của nhóm không phải là huấn luyện một model AI quá lớn, mà là đo lường bằng thực nghiệm: Một thiết bị Edge AI chịu được tối đa bao nhiêu camera cùng lúc, và khi số camera tăng thì hệ thống bắt đầu quá tải và rớt khung hình ở đâu?"*

---

## SLIDE 2: BÀI TOÁN & SENSOR FAILURE CASE THỰC TẾ
* **Nền tảng ứng dụng:** Xe tự hành ADAS / Robot AMR nhà máy thông minh.
* **Tính năng:** Nhận diện vật cản & người đi bộ 360° theo thời gian thực.
* **Cảm biến:** Mảng 4 camera bao quát 4 góc (Trước, Sau, Trái, Phải).
* **Failure Case thực tế:**
  * **Tên lỗi:** Nghẽn băng thông truyền thông & Bão hòa tính toán (Bandwidth & Compute Saturation).
  * **Nguyên nhân:** Camera nạp vào liên tục 30 FPS, nhưng khâu giải nén CPU và GPU tensor không xử lý kịp.
  * **Hậu quả:** Tràn bộ đệm hàng đợi (Buffer Overflow) ➔ Rớt khung hình (Drop Frame) ➔ Mất dấu vật cản, làm chậm phản xạ phanh khẩn cấp.

> **Lời thuyết minh (Speaker Note):**  
> *"Trên xe tự hành, camera gửi luồng video liên tục 30 FPS. Nhưng khi mở rộng lên 4 camera, thiết bị Edge phải đối mặt với áp lực khổng lồ từ cả băng thông nạp vào, tải giải nén CPU và tải suy luận GPU. Nếu không tính toán kịp, hàng đợi sẽ bị tràn, dẫn đến mất khung hình và làm đứt đoạn chuỗi bám vết vật thể nguy hiểm."*

---

## SLIDE 3: KIẾN TRÚC PIPELINE & BỘ ĐO PROFILER
* **Tham chiếu kỹ thuật:** Kiến trúc `nvstreammux` & Bounded Buffer của NVIDIA DeepStream SDK.
* **Cơ chế chống trễ:** Hàng đợi có giới hạn (`bounded queue maxsize=2`). Khi AI bận, frame mới tự động bị loại bỏ (leaky queue) để bảo toàn tính thời gian thực.
* **5 Chỉ số đo đạc theo thời gian thực:**
  1. **FPS per camera:** Tốc độ xuất khung hình thực tế.
  2. **End-to-End Latency:** Đo cả giá trị Average và P95 (mili-giây).
  3. **Drop Frame Rate (%):** Tỷ lệ khung hình bị hủy do tràn hàng đợi.
  4. **CPU & GPU Load (%):** Tải phần cứng đọc qua `psutil` và Windows Performance Counter.
  5. **Ingress Bandwidth (Mbps):** Lưu lượng mạng thực tế nạp vào hệ thống.

> **Lời thuyết minh (Speaker Note):**  
> *"Để đo đạc chính xác, nhóm xây dựng pipeline đa luồng với hàng đợi giới hạn đúng theo khuyến nghị của NVIDIA DeepStream. Bộ Profiler chạy ngầm thu thập liên tục 5 chỉ số và hiển thị lên Web Dashboard qua giao thức WebSocket thời gian thực."*

---

## SLIDE 4: KẾT QUẢ BENCHMARK ĐỐI CHỨNG (THỰC ĐO)
*Dữ liệu trích xuất từ file log `data/benchmark_summary.csv`:*

| Điều kiện | Cấu hình | FPS | Latency P95 | Drop Frame | GPU Load | CPU Load | Ingress Bandwidth | Trạng thái |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline** | 1 Cam 720p | **30.0** | 9.0 ms | **0.0%** | 32.1% | 19.6% | 2.94 Mbps | 🟢 **HEALTHY** |
| **Lỗi A** | 2 Cams 720p | **25.7** | 8.1 ms | **0.0%** | 46.9% | 25.6% | 6.03 Mbps | 🟢 **HEALTHY** |
| **Lỗi B** | 3 Cams 720p | **27.7** | 8.0 ms | **0.0%** | 60.7% | 33.1% | 8.85 Mbps | 🟡 **DEGRADED** |
| **Lỗi C** | 4 Cams 720p | **30.0** | 7.5 ms | **0.0%** | 73.8% | 42.6% | 11.02 Mbps | 🟡 **DEGRADED** |
| **Lỗi D (Stress)** | **4 Cams 1080p** | **25.2** | **10.3 ms** | **5.6%** | **95.7%** | **55.3%** | **23.00 Mbps** | 🔴 **OVERLOAD** |

* **Ước lượng Băng thông thô:**
  $$\text{Raw Bandwidth (4 cams 1080p RGB24)} = 4 \times 1920 \times 1080 \times 30 \times 24\text{ bps} \approx 5.97\text{ Gbps}$$
  ➔ Bắt buộc phải nén H.264 (23 Mbps) vì vượt trần USB 3.0 (3.2 Gbps) và Gigabit Ethernet (1 Gbps).

> **Lời thuyết minh (Speaker Note):**  
> *"Đây là bảng kết quả thực đo từ 460 snapshot. Ở baseline 1 camera 720p, hệ thống chạy êm ở 30 FPS, GPU 32%. Tăng lên 2 và 3 camera, GPU tăng tuyến tính lên 60%. Đến 4 camera 720p, GPU đạt 73.8% vẫn an toàn. Nhưng khi chuyển 4 camera sang 1080p, GPU chạm đỉnh 95.7%, băng thông vọt lên 23 Mbps và kích hoạt trạng thái OVERLOAD với 5.6% drop frame."*

---

## SLIDE 5: PHÂN TÍCH FAILURE CASE & PHÂN ĐỊNH RẠCH RÒI
1. **Hiện tượng nghẽn:** Tại 4 camera 1080p, GPU đạt **95.7%** khiến tốc độ tiêu thụ frame chậm hơn tốc độ nạp 120 FPS của camera, dẫn đến **1,459 frames bị hủy**.
2. **Phân định 3 cấp độ thông tin:**
   * **[Nhóm tự đo]:** Số liệu thực tế GPU 95.7%, CPU 55.3%, Drop 5.6%, Bandwidth 23 Mbps.
   * **[Nguồn tham khảo]:** NVIDIA DeepStream chứng minh khi bão hòa tính toán, bắt buộc dùng leaky queue để giữ độ trễ real-time.
   * **[Suy luận kỹ thuật]:** Rớt 5.6% frame làm đứt đoạn chuỗi bám vết đối tượng, làm chậm phản xạ phanh ADAS thêm 0.5–1.5m.

> **Lời thuyết minh (Speaker Note):**  
> *"Nhóm phân định rất rạch ròi: Mức bão hòa GPU 95.7% và 1,459 frames bị drop là số liệu nhóm đo trực tiếp trên máy. Cơ chế leaky queue là kiến trúc chuẩn từ NVIDIA. Còn tác động làm chậm phanh khẩn cấp là suy luận kỹ thuật của nhóm chứ chưa đo mAP trực tiếp trên xe thật."*

---

## SLIDE 6: ENGINEERING DECISIONS & KHUYẾN NGHỊ TRIỂN KHAI
1. **Xác định giới hạn thiết bị (Capacity Ceiling):** Cấu hình an toàn tối đa cho thiết bị Edge thử nghiệm là **4 Cameras @ 720p 30 FPS** (GPU 73.8%, Drop 0%) hoặc **3 Cameras @ 1080p**.
2. **Giải pháp Hạ tải thích ứng (Adaptive Load Shedding):** Khi `gpu_load > 85%`, hệ thống tự động:
   * Giữ nguyên Camera trước (Critical) ở 1080p @ 30 FPS để nhận diện xa.
   * Hạ 3 camera phụ xung quanh xuống **720p @ 15 FPS**.
   * *Kết quả:* Tiết kiệm ngay 50% băng thông và đưa GPU về mức an toàn **<75%**, triệt tiêu drop frame.
3. **Đề xuất chuẩn phần cứng:** Khuyến nghị dùng giao tiếp **GMSL2 SerDes (3–6 Gbps/link)** cho xe ADAS / Robot AMR thay vì USB 3.0 hay Ethernet dân dụng.

> **Lời thuyết minh (Speaker Note):**  
> *"Từ kết quả trên, nhóm đưa ra 2 quyết định kỹ thuật: Một là xác định ngưỡng trần an toàn là 4 camera 720p. Hai là thuật toán hạ tải thích ứng: khi GPU quá tải, tự động hạ 3 camera phụ xuống 15 FPS, giữ nguyên camera trước để xe luôn an toàn mà không bị quá tải phần cứng."*

---

## SLIDE 7: LIVE DEMO DASHBOARD & KẾT LUẬN
* **Live Demo:** `http://localhost:8000` (Giao diện Cyberpunk Realtime với 4 video feeds, HUD gauges và đồ thị Chart.js).
* **Interactive Slide Deck:** `http://localhost:8000/static/slides.html`
* **Mã nguồn & Dữ liệu:** Đã đồng bộ đầy đủ trên GitHub repository.

> **Lời thuyết minh (Speaker Note):**  
> *"Bây giờ nhóm xin phép mở Dashboard chạy trực tiếp tại localhost 8000 để thầy cô thấy hệ thống chuyển đổi thời gian thực giữa 1, 2, 3 và 4 camera. Nhóm em xin cảm ơn và sẵn sàng trả lời câu hỏi!"*
