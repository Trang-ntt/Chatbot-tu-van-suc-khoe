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
