from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nuoi_cay_mo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'
db = SQLAlchemy(app)

class MauCayMo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ten_mau = db.Column(db.String(100), nullable=False)
    loai_cay = db.Column(db.String(100), nullable=False)
    ngay_cay = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    mo_ta = db.Column(db.Text, nullable=True)
    trang_thai = db.Column(db.String(50), nullable=False)
    phong_id = db.Column(db.Integer, db.ForeignKey('phong_moi_truong.id'), nullable=True)
    phong = db.relationship('PhongMoiTruong', backref='mau_cay_mo')

class PhongMoiTruong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ten_phong = db.Column(db.String(100), nullable=False)
    nhiet_do = db.Column(db.Float, nullable=False)
    do_am = db.Column(db.Float, nullable=False)
    anh_sang = db.Column(db.Float, nullable=False)  # Đơn vị: lux
    trang_thai = db.Column(db.String(50), nullable=False)
    ghi_chu = db.Column(db.Text, nullable=True)
    cap_nhat = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    nhat_ky = db.relationship('NhatKyPhong', backref='phong', lazy='dynamic')

class NhatKyPhong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phong_id = db.Column(db.Integer, db.ForeignKey('phong_moi_truong.id'), nullable=False)
    thoi_gian = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    hanh_dong = db.Column(db.String(100), nullable=False)
    mo_ta = db.Column(db.Text, nullable=True)
    nguoi_thuc_hien = db.Column(db.String(100), nullable=False)
    nhiet_do = db.Column(db.Float, nullable=True)
    do_am = db.Column(db.Float, nullable=True)
    anh_sang = db.Column(db.Float, nullable=True)

# Khởi tạo database
def init_db():
    with app.app_context():
        db.create_all()
        # Kiểm tra và thêm phòng mẫu
        if not PhongMoiTruong.query.first():
            phong_mau = PhongMoiTruong(
                ten_phong='Phòng A1',
                nhiet_do=25.0,
                do_am=70.0,
                anh_sang=1000.0,
                trang_thai='Hoạt động',
                ghi_chu='Phòng nuôi cấy mô thực vật'
            )
            db.session.add(phong_mau)
            db.session.commit()
            
            # Thêm nhật ký mẫu
            nhat_ky_mau = NhatKyPhong(
                phong_id=phong_mau.id,
                hanh_dong='Khởi tạo phòng',
                mo_ta='Thiết lập các thông số ban đầu cho phòng',
                nguoi_thuc_hien='Admin',
                nhiet_do=25.0,
                do_am=70.0,
                anh_sang=1000.0
            )
            db.session.add(nhat_ky_mau)
            db.session.commit()
        
        # Kiểm tra và thêm mẫu cấy demo
        if not MauCayMo.query.first():
            mau_demo = MauCayMo(
                ten_mau='Mẫu Demo',
                loai_cay='Cây Lan',
                mo_ta='Mẫu thử nghiệm',
                trang_thai='Mới tạo',
                phong_id=1
            )
            db.session.add(mau_demo)
            db.session.commit()

@app.route('/')
def trang_chu():
    mau_cay_mo = MauCayMo.query.all()
    return render_template('index.html', mau_cay_mo=mau_cay_mo)

@app.route('/them-mau', methods=['GET', 'POST'])
def them_mau():
    phong_list = PhongMoiTruong.query.all()
    if request.method == 'POST':
        ten_mau = request.form['ten_mau']
        loai_cay = request.form['loai_cay']
        mo_ta = request.form['mo_ta']
        trang_thai = request.form['trang_thai']
        phong_id = request.form.get('phong_id')
        
        mau_moi = MauCayMo(
            ten_mau=ten_mau,
            loai_cay=loai_cay,
            mo_ta=mo_ta,
            trang_thai=trang_thai,
            phong_id=phong_id if phong_id else None
        )
        
        db.session.add(mau_moi)
        db.session.commit()
        return redirect(url_for('trang_chu'))
    
    return render_template('them_mau.html', phong_list=phong_list)

@app.route('/phong-moi-truong')
def danh_sach_phong():
    phong_list = PhongMoiTruong.query.all()
    return render_template('phong_moi_truong/danh_sach.html', phong_list=phong_list)

@app.route('/phong-moi-truong/them', methods=['GET', 'POST'])
def them_phong():
    if request.method == 'POST':
        phong_moi = PhongMoiTruong(
            ten_phong=request.form['ten_phong'],
            nhiet_do=float(request.form['nhiet_do']),
            do_am=float(request.form['do_am']),
            anh_sang=float(request.form['anh_sang']),
            trang_thai=request.form['trang_thai'],
            ghi_chu=request.form['ghi_chu']
        )
        db.session.add(phong_moi)
        db.session.commit()

        # Thêm nhật ký
        nhat_ky = NhatKyPhong(
            phong_id=phong_moi.id,
            hanh_dong='Tạo phòng mới',
            mo_ta=f'Khởi tạo phòng {phong_moi.ten_phong}',
            nguoi_thuc_hien=request.form.get('nguoi_thuc_hien', 'Admin'),
            nhiet_do=phong_moi.nhiet_do,
            do_am=phong_moi.do_am,
            anh_sang=phong_moi.anh_sang
        )
        db.session.add(nhat_ky)
        db.session.commit()

        return redirect(url_for('danh_sach_phong'))
    
    return render_template('phong_moi_truong/them.html')

@app.route('/phong-moi-truong/<int:id>')
def chi_tiet_phong(id):
    phong = PhongMoiTruong.query.get_or_404(id)
    nhat_ky = NhatKyPhong.query.filter_by(phong_id=id).order_by(NhatKyPhong.thoi_gian.desc()).all()
    return render_template('phong_moi_truong/chi_tiet.html', phong=phong, nhat_ky=nhat_ky)

@app.route('/phong-moi-truong/<int:id>/cap-nhat', methods=['GET', 'POST'])
def cap_nhat_phong(id):
    phong = PhongMoiTruong.query.get_or_404(id)
    if request.method == 'POST':
        nhiet_do_moi = float(request.form['nhiet_do'])
        do_am_moi = float(request.form['do_am'])
        anh_sang_moi = float(request.form['anh_sang'])
        trang_thai_moi = request.form['trang_thai']
        
        # Cập nhật thông tin phòng
        phong.nhiet_do = nhiet_do_moi
        phong.do_am = do_am_moi
        phong.anh_sang = anh_sang_moi
        phong.trang_thai = trang_thai_moi
        phong.ghi_chu = request.form['ghi_chu']
        phong.cap_nhat = datetime.utcnow()
        
        # Thêm nhật ký
        nhat_ky = NhatKyPhong(
            phong_id=phong.id,
            hanh_dong='Cập nhật thông số',
            mo_ta=request.form.get('mo_ta_nhat_ky', 'Cập nhật thông số môi trường'),
            nguoi_thuc_hien=request.form.get('nguoi_thuc_hien', 'Admin'),
            nhiet_do=nhiet_do_moi,
            do_am=do_am_moi,
            anh_sang=anh_sang_moi
        )
        
        db.session.add(nhat_ky)
        db.session.commit()
        return redirect(url_for('chi_tiet_phong', id=id))
    
    return render_template('phong_moi_truong/cap_nhat.html', phong=phong)

@app.route('/phong-moi-truong/<int:id>/nhat-ky')
def nhat_ky_phong(id):
    phong = PhongMoiTruong.query.get_or_404(id)
    nhat_ky = NhatKyPhong.query.filter_by(phong_id=id).order_by(NhatKyPhong.thoi_gian.desc()).all()
    return render_template('phong_moi_truong/nhat_ky.html', phong=phong, nhat_ky=nhat_ky)

# Khởi tạo database khi khởi động ứng dụng
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 