# Changelog

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
