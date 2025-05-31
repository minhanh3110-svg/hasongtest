from app import app, db

with app.app_context():
    # Xóa tất cả các bảng cũ nếu có
    db.drop_all()
    
    # Tạo lại tất cả các bảng
    db.create_all()
    
    print("Database đã được khởi tạo thành công!") 