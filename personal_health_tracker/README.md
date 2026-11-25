# Ứng dụng theo dõi sức khỏe cá nhân

Ứng dụng FastAPI + SQLite phục vụ đồ án Chủ đề 3. Đây là module độc lập đặt trong repository HealthBot hiện có để không làm hỏng các chức năng cũ.

## Chức năng
- Đăng ký, đăng nhập bằng JWT; vai trò `admin`, `user`, `viewer`.
- Hồ sơ cá nhân: ngày sinh, giới tính, chiều cao, tiền sử, mục tiêu.
- Nhập thủ công và CSV: huyết áp (tâm thu/tâm trương), cân nặng, đường huyết, nhịp tim, giấc ngủ.
- Ngưỡng cảnh báo do người dùng cấu hình, có tên nguồn tham khảo và URL; cảnh báo khi vượt ngưỡng hoặc thay đổi đột ngột.
- Xu hướng ngày/tuần/tháng: trung bình trượt, hồi quy tuyến tính, Z-score khi đủ dữ liệu.
- Nhắc đo chỉ số, uống thuốc, vận động.
- Chia sẻ dữ liệu với tài khoản viewer bằng sự đồng ý rõ ràng; có thể thu hồi.
- Xuất Excel và PDF.
- Dữ liệu demo hoàn toàn giả lập.

## Chạy trên Windows
Mở terminal tại thư mục repository:

```powershell
cd personal_health_tracker
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Mở http://127.0.0.1:8000 và tài liệu API tại http://127.0.0.1:8000/docs.

Đặt `JWT_SECRET` trong file `.env` thành chuỗi ngẫu nhiên dài tối thiểu 32 ký tự trước khi dùng ngoài demo. Không commit file `.env`.

## Tạo tài khoản demo (dữ liệu giả lập)
Trong terminal thứ hai:

```powershell
python -m app.seed_demo
```

Tài khoản:
- Admin: `admin_demo` / `AdminDemo!2026`
- Người dùng: `user_demo` / `UserDemo!2026`
- Người thân/bác sĩ xem được chia sẻ: `viewer_demo` / `ViewerDemo!2026`

Chỉ dùng các tài khoản và dữ liệu này để trình diễn. Đổi mật khẩu và JWT secret trước khi triển khai thực tế.

## API chính
| Nhóm | Endpoint |
|---|---|
| Auth | `POST /api/auth/register`, `POST /api/auth/login` |
| Hồ sơ | `GET/PUT /api/profile` |
| Chỉ số | `GET/POST /api/metrics`, `DELETE /api/metrics/{id}`, `POST /api/metrics/import-csv` |
| Ngưỡng/cảnh báo | `GET/POST /api/thresholds`, `GET /api/alerts` |
| AI xu hướng | `GET /api/analytics/trends?metric=weight&period=week` |
| Nhắc nhở | `GET/POST /api/reminders`, `DELETE /api/reminders/{id}` |
| Chia sẻ | `GET/POST /api/shares`, `DELETE /api/shares/{id}`, `GET /api/shared/{owner_id}/metrics` |
| Báo cáo | `GET /api/reports/export.xlsx`, `GET /api/reports/export.pdf` |

## Bảo mật và giới hạn
- Mỗi truy vấn dữ liệu cá nhân được lọc theo user id từ JWT; không tin user id truyền từ trình duyệt.
- Viewer chỉ xem các chỉ số của chủ tài khoản khi có bản ghi chia sẻ đang hiệu lực và đúng phạm vi quyền.
- Admin quản lý hệ thống; không mặc định được đọc dữ liệu sức khỏe riêng tư.
- Ngưỡng là cấu hình tham khảo, không phải chẩn đoán. Huyết áp/đường huyết phụ thuộc tuổi, bệnh nền, thời điểm đo và hướng dẫn chuyên môn; không dùng một ngưỡng chung cho mọi người.
- Cảnh báo nguy hiểm cần liên hệ cơ sở y tế/cấp cứu tại địa phương; ứng dụng không chẩn đoán, không kê đơn.
- Phân tích AI trong bản này là thuật toán giải thích xu hướng (moving average, linear regression, Z-score), không phải mô hình chẩn đoán và không gọi LLM API.
- Nhắc nhở hiện được lưu và hiển thị trong ứng dụng; chưa có dịch vụ gửi push/email/SMS nền.

## Nguồn tham khảo ngưỡng và khuyến nghị
Các nguồn dưới đây được đưa vào tài liệu để người làm đồ án tra cứu và ghi nguồn cho cấu hình phù hợp. Không mã hóa các ngưỡng này thành kết luận y khoa cố định:
1. WHO – Hypertension: https://www.who.int/news-room/fact-sheets/detail/hypertension
2. WHO – Diabetes: https://www.who.int/news-room/fact-sheets/detail/diabetes
3. WHO – Physical activity: https://www.who.int/news-room/fact-sheets/detail/physical-activity
4. CDC – About Sleep: https://www.cdc.gov/sleep/about/index.html

## Kiểm thử
Chạy: `pytest -q`. Xem `docs/TEST_PLAN.md` và `docs/AI_USAGE.md`.
