# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from sqlalchemy import func

app = Flask(__name__)

# Cấu hình database
database_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
    SQLALCHEMY_DATABASE_URI=database_url,
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = SQLAlchemy(app)

# Models
class Mau(db.Model):
    __tablename__ = 'mau'
    id = db.Column(db.Integer, primary_key=True)
    ma_mau = db.Column(db.String(50), unique=True, nullable=False)
    ten = db.Column(db.String(100), nullable=False)
    mo_ta = db.Column(db.Text)
    ngay_cay = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    trang_thai = db.Column(db.String(50))
    phong_id = db.Column(db.Integer, db.ForeignKey('phong.id'), nullable=False)
    nhat_ky = db.relationship('NhatKy', backref='mau', lazy=True)

class Phong(db.Model):
    __tablename__ = 'phong'
    id = db.Column(db.Integer, primary_key=True)
    ten = db.Column(db.String(100), nullable=False)
    nhiet_do = db.Column(db.Float)
    do_am = db.Column(db.Float)
    mau_list = db.relationship('Mau', backref='phong', lazy=True)

class NhatKy(db.Model):
    __tablename__ = 'nhat_ky'
    id = db.Column(db.Integer, primary_key=True)
    mau_id = db.Column(db.Integer, db.ForeignKey('mau.id'), nullable=False)
    ngay_ghi = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    noi_dung = db.Column(db.Text, nullable=False)

# Template filters
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
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    room = request.args.get('room', '')
    query = Mau.query
    if search:
        query = query.filter(Mau.ten.ilike(f'%{search}%'))
    if status:
        query = query.filter(Mau.trang_thai == status)
    if room:
        query = query.filter(Mau.phong_id == room)
    stats = {
        'new_count': Mau.query.filter_by(trang_thai='Mới tạo').count(),
        'developing_count': Mau.query.filter_by(trang_thai='Đang phát triển').count(),
        'completed_count': Mau.query.filter_by(trang_thai='Đã hoàn thành').count(),
        'failed_count': Mau.query.filter_by(trang_thai='Thất bại').count()
    }
    room_stats = db.session.query(
        Phong.ten.label('name'),
        func.count(Mau.id).label('count')
    ).outerjoin(Mau).group_by(Phong.id, Phong.ten).all()
    mau_pagination = query.order_by(Mau.ngay_cay.desc()).paginate(page=page, per_page=per_page)
    rooms = Phong.query.all()
    return render_template('index.html',
                         mau_pagination=mau_pagination,
                         stats=stats,
                         room_stats=room_stats,
                         rooms=rooms)

@app.route('/them-mau-moi', methods=['GET', 'POST'])
def them_mau_moi():
    if request.method == 'POST':
        ma_mau = request.form.get('ma_mau')
        ten = request.form.get('ten_mau')
        mo_ta = request.form.get('mo_ta')
        phong_id = request.form.get('phong_id')
        trang_thai = request.form.get('trang_thai', 'Mới tạo')
        if not all([ma_mau, ten, phong_id]):
            flash('Vui lòng điền đủ thông tin bắt buộc', 'error')
            return redirect(url_for('them_mau_moi'))
        try:
            mau_moi = Mau(
                ma_mau=ma_mau,
                ten=ten,
                mo_ta=mo_ta,
                phong_id=phong_id,
                trang_thai=trang_thai
            )
            db.session.add(mau_moi)
            db.session.commit()
            flash('Thêm mẫu mới thành công!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
            return redirect(url_for('them_mau_moi'))

    phong_list = Phong.query.all()
    return render_template('them_mau.html', phong_list=phong_list)

# ... giữ nguyên các route còn lại ...
