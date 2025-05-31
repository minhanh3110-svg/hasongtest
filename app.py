from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from sqlalchemy import func

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nuoi_cay_mo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Phong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ten = db.Column(db.String(100), nullable=False)
    mo_ta = db.Column(db.Text)
    mau = db.relationship('Mau', backref='phong', lazy=True)

class Mau(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ten = db.Column(db.String(100), nullable=False)
    mo_ta = db.Column(db.Text)
    ngay_cay = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    trang_thai = db.Column(db.String(50), nullable=False, default='Mới tạo')
    phong_id = db.Column(db.Integer, db.ForeignKey('phong.id'), nullable=False)
    nhat_ky = db.relationship('NhatKy', backref='mau', lazy=True)

class NhatKy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    noi_dung = db.Column(db.Text, nullable=False)
    ngay_ghi = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    mau_id = db.Column(db.Integer, db.ForeignKey('mau.id'), nullable=False)

# Jinja filters
@app.template_filter('status_color')
def status_color(status):
    colors = {
        'Mới tạo': 'success',
        'Đang phát triển': 'primary',
        'Đã hoàn thành': 'warning',
        'Thất bại': 'danger'
    }
    return colors.get(status, 'secondary')

# Routes
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 9
    
    # Lấy các tham số tìm kiếm
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    room = request.args.get('room', '')
    
    # Query cơ bản
    query = Mau.query
    
    # Áp dụng các bộ lọc
    if search:
        query = query.filter(Mau.ten.ilike(f'%{search}%'))
    if status:
        query = query.filter(Mau.trang_thai == status)
    if room:
        query = query.filter(Mau.phong_id == room)
    
    # Phân trang
    mau_pagination = query.order_by(Mau.ngay_cay.desc()).paginate(page=page, per_page=per_page)
    
    # Thống kê trạng thái
    stats = {
        'new_count': Mau.query.filter_by(trang_thai='Mới tạo').count(),
        'developing_count': Mau.query.filter_by(trang_thai='Đang phát triển').count(),
        'completed_count': Mau.query.filter_by(trang_thai='Đã hoàn thành').count(),
        'failed_count': Mau.query.filter_by(trang_thai='Thất bại').count()
    }
    
    # Thống kê theo phòng
    room_stats = db.session.query(
        Phong.ten.label('name'),
        func.count(Mau.id).label('count')
    ).join(Mau).group_by(Phong.id).all()
    
    # Lấy danh sách phòng cho bộ lọc
    rooms = Phong.query.all()
    
    return render_template('index.html',
                         mau_pagination=mau_pagination,
                         stats=stats,
                         room_stats=room_stats,
                         rooms=rooms)

@app.route('/them-mau-moi', methods=['GET', 'POST'])
def them_mau_moi():
    if request.method == 'POST':
        ten = request.form.get('ten')
        mo_ta = request.form.get('mo_ta')
        phong_id = request.form.get('phong_id')
        
        if not all([ten, phong_id]):
            flash('Vui lòng điền đầy đủ thông tin bắt buộc', 'error')
            return redirect(url_for('them_mau_moi'))
        
        mau = Mau(
            ten=ten,
            mo_ta=mo_ta,
            phong_id=phong_id
        )
        
        try:
            db.session.add(mau)
            db.session.commit()
            flash('Thêm mẫu mới thành công!', 'success')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            flash('Có lỗi xảy ra khi thêm mẫu mới', 'error')
    
    phong = Phong.query.all()
    return render_template('them_mau_moi.html', phong=phong)

@app.route('/cap-nhat-mau/<int:id>', methods=['GET', 'POST'])
def cap_nhat_mau(id):
    mau = Mau.query.get_or_404(id)
    
    if request.method == 'POST':
        mau.ten = request.form.get('ten')
        mau.mo_ta = request.form.get('mo_ta')
        mau.trang_thai = request.form.get('trang_thai')
        mau.phong_id = request.form.get('phong_id')
        
        try:
            db.session.commit()
            
            # Thêm nhật ký nếu có ghi chú
            ghi_chu = request.form.get('ghi_chu')
            if ghi_chu:
                nhat_ky = NhatKy(
                    noi_dung=ghi_chu,
                    mau_id=mau.id
                )
                db.session.add(nhat_ky)
                db.session.commit()
            
            flash('Cập nhật mẫu thành công!', 'success')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            flash('Có lỗi xảy ra khi cập nhật mẫu', 'error')
    
    phong = Phong.query.all()
    return render_template('cap_nhat_mau.html', mau=mau, phong=phong)

@app.route('/chi-tiet-mau/<int:id>')
def chi_tiet_mau(id):
    mau = Mau.query.get_or_404(id)
    return render_template('chi_tiet_mau.html', mau=mau)

@app.route('/xoa-mau/<int:id>')
def xoa_mau(id):
    mau = Mau.query.get_or_404(id)
    
    try:
        db.session.delete(mau)
        db.session.commit()
        flash('Xóa mẫu thành công!', 'success')
    except:
        db.session.rollback()
        flash('Có lỗi xảy ra khi xóa mẫu', 'error')
    
    return redirect(url_for('index'))

@app.route('/phong-moi-truong')
def phong_moi_truong():
    phong = Phong.query.all()
    return render_template('phong_moi_truong.html', phong=phong)

@app.route('/them-phong-moi', methods=['GET', 'POST'])
def them_phong_moi():
    if request.method == 'POST':
        ten = request.form.get('ten')
        mo_ta = request.form.get('mo_ta')
        
        if not ten:
            flash('Vui lòng nhập tên phòng', 'error')
            return redirect(url_for('them_phong_moi'))
        
        phong = Phong(
            ten=ten,
            mo_ta=mo_ta
        )
        
        try:
            db.session.add(phong)
            db.session.commit()
            flash('Thêm phòng mới thành công!', 'success')
            return redirect(url_for('phong_moi_truong'))
        except:
            db.session.rollback()
            flash('Có lỗi xảy ra khi thêm phòng mới', 'error')
    
    return render_template('them_phong_moi.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 