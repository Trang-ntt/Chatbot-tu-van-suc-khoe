# Minh chứng sử dụng AI

Đây là mẫu ghi chép; nhóm cần bổ sung prompt, ảnh chụp, ngày thực hiện và kết quả thực tế. Không ghi nhận hoạt động chưa diễn ra.

## 1. Khảo sát và phân tích
AI hỗ trợ gợi ý tác nhân, yêu cầu chức năng/phi chức năng, tình huống nhập số đo, cảnh báo, quyền riêng tư và đồng ý chia sẻ. Nhóm phải đối chiếu bằng khảo sát và chốt yêu cầu cuối cùng.

## 2. Thiết kế
AI hỗ trợ rà soát user flow, schema SQLite, quan hệ người dùng–chỉ số–ngưỡng–cảnh báo–chia sẻ và ma trận quyền. Nhóm tự xác nhận ERD và kiểm tra luồng thu hồi consent.

## 3. Lập trình và kiểm thử
AI hỗ trợ tạo khung FastAPI/SQLite, thuật toán thống kê giải thích được và ca kiểm thử. Nhóm cần chạy, sửa, ghi lại lỗi và hiểu từng hàm trước khi trình bày.

## Phần AI trong sản phẩm
Sản phẩm sử dụng trung bình trượt, hồi quy tuyến tính OLS và Z-score. Đây là phân tích thống kê xu hướng, không phải mô hình chẩn đoán, không dự đoán bệnh và không gọi LLM API. Các đoạn giải thích được sinh theo mẫu dựa trên chiều hướng dữ liệu.

## Công khai phần AI hỗ trợ sinh
Các tệp `app/main.py`, `app/analytics.py`, `app/db.py`, `tests/test_analytics.py` có nội dung được AI hỗ trợ tạo/gợi ý. Nhóm phải đọc, kiểm thử, chỉnh sửa và giải thích luồng chạy.

## Nguồn tham khảo để nhóm xác minh
- WHO – Hypertension: https://www.who.int/news-room/fact-sheets/detail/hypertension
- WHO – Diabetes: https://www.who.int/news-room/fact-sheets/detail/diabetes
- WHO – Physical activity: https://www.who.int/news-room/fact-sheets/detail/physical-activity
- CDC – Sleep: https://www.cdc.gov/sleep/about/index.html

Ngưỡng trong ứng dụng do người dùng cấu hình kèm nguồn và bối cảnh, không gán một giá trị bình thường duy nhất cho mọi người. Lời khuyên chỉ tham khảo, không thay thế bác sĩ.


## Chatbot phân tích triệu chứng và trợ lý cá nhân (bổ sung trong nhánh tích hợp)

- Mô hình phân tích triệu chứng: tái sử dụng tệp mô hình mo_hinh.npz, bot.py, tu_dien.csv, dong_nghia.csv và phan_loai_do_tuoi.csv từ nhánh chatbot.
- Mô hình hiện xếp hạng bệnh theo mức độ phù hợp tương đối dựa trên triệu chứng được trích xuất; điểm phần trăm không phải xác suất mắc bệnh thực tế.
- Khách truy cập dùng endpoint /api/symptoms/* với phiên khách riêng, không truy cập hồ sơ hoặc chỉ số cá nhân.
- Người dùng đăng nhập dùng endpoint /api/assistant/*; server lấy hồ sơ và chỉ số theo user id trong JWT, không nhận user id từ trình duyệt.
- Tuổi/giới dùng để cung cấp thông tin nhóm tuổi tham khảo; không điều chỉnh điểm mô hình vì chưa có cơ sở hiệu chỉnh đáng tin cậy.
- Các nội dung tư vấn và giao diện tích hợp được AI hỗ trợ tạo; nhóm cần rà soát, chạy test và chịu trách nhiệm kiểm chứng. Không xem AI là nguồn xác nhận y khoa.
