# User Flow và phân quyền

## Luồng người dùng
1. Đăng ký/đăng nhập → nhận JWT.
2. Cập nhật hồ sơ cá nhân.
3. Ghi chỉ số hoặc nhập CSV → kiểm tra dữ liệu → lưu SQLite.
4. Hệ thống so ngưỡng do chính người dùng cấu hình và kiểm tra thay đổi đột ngột → tạo cảnh báo.
5. Chọn loại chỉ số/khoảng thời gian → trung bình trượt, hồi quy tuyến tính, Z-score → hiển thị xu hướng tham khảo.
6. Tạo nhắc đo/thuốc/vận động.
7. Tự nguyện chia sẻ cho tài khoản viewer → lưu consent; có thể thu hồi.
8. Xuất báo cáo Excel/PDF.

## Ma trận quyền
| Chức năng | Admin | User | Viewer |
|---|---:|---:|---:|
| Xem danh sách tài khoản | Có | Không | Không |
| Sửa hồ sơ cá nhân | Không | Của mình | Không |
| Nhập/xóa số đo | Không | Của mình | Không |
| Cấu hình ngưỡng/nhắc nhở | Không | Của mình | Không |
| Đọc số đo được chia sẻ | Không mặc định | Của mình | Có consent còn hiệu lực |
| Thu hồi chia sẻ | Không | Của mình | Không |

Viewer không có quyền tự cấp quyền cho mình. Chủ dữ liệu là người quyết định chia sẻ và thu hồi.