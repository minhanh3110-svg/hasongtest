from app import db

def init_db():
    # Tạo tất cả các bảng
    db.create_all()
    print("Đã tạo database thành công!")

if __name__ == '__main__':
    init_db() 