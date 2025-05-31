from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nuoi_cay_mo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MauCayMo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ten_mau = db.Column(db.String(100), nullable=False)
    loai_cay = db.Column(db.String(100), nullable=False)
    ngay_cay = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    mo_ta = db.Column(db.Text, nullable=True)
    trang_thai = db.Column(db.String(50), nullable=False)

@app.route('/')
def trang_chu():
    mau_cay_mo = MauCayMo.query.all()
    return render_template('index.html', mau_cay_mo=mau_cay_mo)

@app.route('/them-mau', methods=['GET', 'POST'])
def them_mau():
    if request.method == 'POST':
        ten_mau = request.form['ten_mau']
        loai_cay = request.form['loai_cay']
        mo_ta = request.form['mo_ta']
        trang_thai = request.form['trang_thai']
        
        mau_moi = MauCayMo(
            ten_mau=ten_mau,
            loai_cay=loai_cay,
            mo_ta=mo_ta,
            trang_thai=trang_thai
        )
        
        db.session.add(mau_moi)
        db.session.commit()
        return redirect(url_for('trang_chu'))
    
    return render_template('them_mau.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 