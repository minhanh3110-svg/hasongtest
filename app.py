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
        return redirect(url_for('danh_sach_phong'))
    
    return render_template('phong_moi_truong/them.html')

@app.route('/phong-moi-truong/<int:id>')
def chi_tiet_phong(id):
    phong = PhongMoiTruong.query.get_or_404(id)
    return render_template('phong_moi_truong/chi_tiet.html', phong=phong)

@app.route('/phong-moi-truong/<int:id>/cap-nhat', methods=['GET', 'POST'])
def cap_nhat_phong(id):
    phong = PhongMoiTruong.query.get_or_404(id)
    if request.method == 'POST':
        phong.nhiet_do = float(request.form['nhiet_do'])
        phong.do_am = float(request.form['do_am'])
        phong.anh_sang = float(request.form['anh_sang'])
        phong.trang_thai = request.form['trang_thai']
        phong.ghi_chu = request.form['ghi_chu']
        phong.cap_nhat = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('chi_tiet_phong', id=id))
    
    return render_template('phong_moi_truong/cap_nhat.html', phong=phong)

# Khởi tạo database khi khởi động ứng dụng
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 