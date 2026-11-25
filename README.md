# Ứng dụng theo dõi sức khỏe cá nhân

Repository này dùng **Personal Health Tracker** làm ứng dụng chính. Chatbot cũ được gỡ khỏi ứng dụng ở nhánh `main`; nhánh `chatbot` được giữ riêng, không trộn chatbot cũ vào luồng theo dõi sức khỏe.

## Chạy nhanh trên Windows

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item personal_health_tracker/.env.example .env
```

Mở `.env`, thay `JWT_SECRET` bằng chuỗi ngẫu nhiên dài tối thiểu 32 ký tự. Sau đó chạy:

```powershell
python -m personal_health_tracker.app.seed_demo
uvicorn main:app --reload
```

Mở http://127.0.0.1:8000 hoặc tài liệu API tại http://127.0.0.1:8000/docs.

## Tài khoản dữ liệu giả lập

- Admin: `admin_demo` / `AdminDemo!2026`
- User: `user_demo` / `UserDemo!2026`
- Viewer: `viewer_demo` / `ViewerDemo!2026`

Đổi mật khẩu demo trước khi trình diễn nếu ứng dụng được chia sẻ ra ngoài. Không nhập dữ liệu sức khỏe thật.

## Chạy kiểm thử

```powershell
cd personal_health_tracker
pytest -q
```

GitHub Actions tự chạy kiểm thử khi có Pull Request hoặc cập nhật nhánh `main`.

## Triển khai website

Có sẵn `render.yaml` cho Render. Tạo Web Service/Blueprint từ repository, chọn cấu hình trong `render.yaml`. Render tạo `JWT_SECRET` tự động. Với demo miễn phí, SQLite nằm trên ổ đĩa tạm và dữ liệu có thể mất khi service khởi động lại hoặc deploy lại; chỉ dùng dữ liệu giả lập.

Để URL website xuất hiện trong tab Actions, vào Settings → Secrets and variables → Actions:
- Thêm secret `RENDER_DEPLOY_HOOK_URL` (Deploy Hook URL lấy từ Render).
- Thêm variable `DEPLOYED_APP_URL` (URL website Render).

Sau khi merge lên `main`, workflow kiểm thử rồi gọi Render deploy hook; URL website được ghi vào phần Summary của lần chạy Actions.

## An toàn và giới hạn

- Chỉ dữ liệu giả lập; ứng dụng không chẩn đoán, không kê đơn.
- Ngưỡng cảnh báo do người dùng cấu hình, phải ghi rõ nguồn và bối cảnh; không dùng một ngưỡng chung cho mọi người.
- Viewer chỉ xem dữ liệu khi chủ tài khoản chủ động đồng ý; có thể thu hồi.
- Admin quản lý tài khoản và vai trò, không mặc định được xem hồ sơ/số đo sức khỏe.
- Phân tích AI là trung bình trượt, hồi quy tuyến tính OLS và Z-score; chỉ mô tả xu hướng thống kê.
- Xem `personal_health_tracker/docs/` để biết ERD, User Flow, kế hoạch kiểm thử và minh chứng sử dụng AI.
