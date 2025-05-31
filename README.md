# Ứng dụng Quản lý Nuôi Cấy Mô

Ứng dụng web để quản lý các mẫu nuôi cấy mô thực vật, được xây dựng bằng Python Flask.

## Tính năng

- Quản lý mẫu nuôi cấy:
  - Xem danh sách mẫu với phân trang và tìm kiếm
  - Thêm mẫu mới
  - Cập nhật thông tin mẫu
  - Xóa mẫu
  - Theo dõi trạng thái mẫu (Mới tạo, Đang phát triển, Đã hoàn thành, Thất bại)

- Quản lý nhật ký:
  - Thêm nhật ký theo dõi cho từng mẫu
  - Xem lịch sử nhật ký theo thời gian

- Thống kê và báo cáo:
  - Biểu đồ thống kê trạng thái mẫu
  - Biểu đồ phân bố mẫu theo phòng

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/minhanh3110-svg/hasongtest.git
cd hasongtest
```

2. Tạo và kích hoạt môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Cài đặt các thư viện:
```bash
pip install -r requirements.txt
```

4. Khởi tạo database:
```bash
python init_db.py
```

5. Chạy ứng dụng:
```bash
flask run
```

## Công nghệ sử dụng

- Backend:
  - Python Flask
  - SQLAlchemy ORM
  - PostgreSQL/SQLite

- Frontend:
  - Bootstrap 5
  - Chart.js
  - Font Awesome
  - jQuery
  - Toastr

## Cấu trúc thư mục

```
hasongtest/
├── static/
│   └── css/
│       └── style.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── them_mau_moi.html
│   ├── chi_tiet_mau.html
│   └── cap_nhat_mau.html
├── app.py
├── init_db.py
├── requirements.txt
├── runtime.txt
└── README.md
```

## Triển khai

Ứng dụng được triển khai trên Render.com với các cấu hình:

- Build Command: `pip install -r requirements.txt && python init_db.py`
- Start Command: `gunicorn app:app`
- Environment Variables:
  - PYTHON_VERSION=3.9.7
  - DATABASE_URL=postgresql://...
  - FLASK_APP=app.py
  - FLASK_ENV=production
  - SECRET_KEY=your-secret-key

## Đóng góp

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## Giấy phép

Phân phối dưới giấy phép MIT. Xem `LICENSE` để biết thêm thông tin.

## Liên hệ

Minh Anh - [@minhanh3110-svg](https://github.com/minhanh3110-svg) 