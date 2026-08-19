# Changelog

## v1.3.0 — 2026-08-19

- Nâng version ứng dụng lên `v1.3.0`.
- Đưa cột `LP khả dụng` lên giữa `Email` và `Group ID` để dễ theo dõi số LP ngay cạnh tài khoản.
- Cập nhật hiệu ứng hover bảng: khi rê chuột vào bất kỳ ô nào, toàn bộ dòng được tô xanh.
- Khi rời chuột khỏi bảng hoặc tắt hover, dòng tự trả về màu mặc định.
- Đồng bộ màu hover/reset cho cả giao diện dark và light.
- Áp dụng hover cả dòng cho cả bảng chính `Tài khoản & Chạy` và tab `Acc DIE`.
- Khi đổi theme dark/light, bảng tự refresh lại màu để không bị giữ style cũ.

## v1.2.0 — 2026-08-19

- Thêm cơ chế **Acc DIE mềm** trong `accounts.json`: `is_dead`, `dead_reason`, `dead_at`, `dead_source`, `dead_count`, `last_error`.
- Tự nhận diện lỗi login nghiêm trọng và chỉ đánh dấu DIE sau 2 lần lỗi liên tiếp.
- Không đánh dấu DIE với lỗi tạm như không lấy được OTP, proxy, timeout hoặc lỗi mạng.
- Thêm tab **Acc DIE** để xem, tìm kiếm, khôi phục, xuất Excel và xóa vĩnh viễn tài khoản chết.
- Thêm nút/menu chuột phải để đánh dấu DIE hoặc khôi phục account thủ công.
- Tự bỏ qua thao tác chạy/check/tạo LP/xem LP với account đã nằm trong danh sách DIE.
- Cập nhật login để lỗi đăng nhập thất bại trả về đúng dạng lỗi login, tránh bị nhầm thành lỗi OTP.

## v1.1.0 — 2026-08-18

- Thêm tab **GetCode**: nhập email, tự đọc OTP LinksMate từ Gmail đã cấu hình, hiển thị và sao chép mã.
- Giảm số lần kiểm tra OTP mặc định từ 10 xuống 5 lần.
- Tách dữ liệu LP thành `lp_balance` (LP khả dụng) và `lp_code` (mã LP 6 ký tự); migrate dữ liệu trong `accounts.json`.
- Sửa lỗi mã LP bị ghi nhầm vào cột Số điện thoại và trạng thái bị ghi nhầm vào cột Email.
- Khi Check nhóm, lấy thông tin người dùng từ `registrationinfo`: họ/tên, kana, romaji, địa chỉ, mã bưu điện và số điện thoại.
- Cập nhật parser cho cấu trúc label/value của trang `registrationinfo`.
- Đưa cột LP khả dụng về giữa EID và Mã số LP (6 ký tự).
- Log request mặc định thu gọn, có nút mở/thu gọn trên thanh công cụ.
- Tắt tự cuộn bảng khi chỉ rê chuột hoặc kéo dòng sát mép bảng.
- Tối ưu Check nhóm: chỉ login/OTP một lần, tái sử dụng session để đổi group và bỏ request SIM bị trùng.
