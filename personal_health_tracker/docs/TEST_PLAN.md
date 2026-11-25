# Kế hoạch kiểm thử

Chỉ dùng dữ liệu giả lập. Chạy tại thư mục dự án: `pytest -q`.

| ID | Ca kiểm thử | Kết quả mong đợi |
|---|---|---|
| T01 | Đăng nhập hợp lệ | JWT và vai trò |
| T02 | Sai mật khẩu | HTTP 401 |
| T03 | Username trùng | HTTP 409 |
| T04 | User đọc hồ sơ của mình | Thành công |
| T05 | Viewer gọi API user-only | HTTP 403 |
| T06 | Huyết áp thiếu tâm trương | HTTP 400 |
| T07 | Ghi số đo | Lưu đúng chủ sở hữu |
| T08 | Vượt ngưỡng đã cài | Sinh cảnh báo |
| T09 | CSV lỗi | Bỏ qua dòng không hợp lệ |
| T10 | Chuỗi dữ liệu tăng/giảm | Phân loại xu hướng |
| T11 | Viewer chưa được cấp quyền | HTTP 403 |
| T12 | User đồng ý chia sẻ | Viewer đọc được số đo |
| T13 | User thu hồi chia sẻ | Viewer bị HTTP 403 |
| T14 | User A đọc dữ liệu User B | Không truy cập được |
| T15 | Xuất Excel | Tải được tệp |

Kiểm thử bảo mật: token sai/hết hạn phải bị từ chối; mọi truy vấn riêng tư lọc theo ID lấy từ JWT; viewer cần consent còn hiệu lực; admin không mặc nhiên được xem số đo riêng tư.

Cần bổ sung kiểm thử tích hợp bằng TestClient trước khi nghiệm thu cuối cùng.
