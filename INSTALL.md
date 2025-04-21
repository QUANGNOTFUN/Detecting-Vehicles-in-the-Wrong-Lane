# Hướng dẫn cài đặt

## Cài đặt các thư viện cần thiết

Để cài đặt tất cả các thư viện cần thiết cho dự án, chạy lệnh sau trong terminal:

```bash
python -m pip install -r requirements.txt
```

Lệnh này sẽ tự động cài đặt:
- ultralytics (phiên bản 8.2.0)
- opencv-python
- pillow (phiên bản 10.2.0)
- paddlepaddle
- paddleocr

## Xử lý lỗi thường gặp

1. Cảnh báo về ccache:
   - Đây chỉ là cảnh báo, không ảnh hưởng đến chức năng chính
   - Nếu muốn tắt cảnh báo, có thể cài đặt ccache từ: https://github.com/ccache/ccache/blob/master/doc/INSTALL.md

2. Lỗi tokenizing data:
   - Kiểm tra định dạng file dữ liệu (CSV, JSON, etc.)
   - Đảm bảo số lượng cột trong file dữ liệu khớp với yêu cầu của chương trình 