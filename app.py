import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# سر استقرار الجلسة ومنع الانهيار
app.secret_key = os.environ.get('SECRET_KEY', 'MAHJOUB_2026_GOLDEN_KEY')

# 1. إعدادات قاعدة البيانات (Railway Postgres)
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 2. تعريف النماذج (Models) - الاعتماد على الجداول المفردة
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100))
    wallet_address = db.Column(db.String(100))

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))

# 3. المسارات الأساسية (Core Routes)
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        # التحقق من المورد في قاعدة البيانات
        vendor = Vendor.query.filter_by(username=u, password=p).first()
        if vendor:
            session['vendor_id'] = vendor.id
            return redirect(url_for('dashboard'))
        flash("بيانات الدخول غير صحيحة")
    return render_template('login.html')

# 4. لوحة التحكم (The Dashboard) - المنطقة الحساسة
@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # جلب البيانات لضمان عدم ظهور خطأ 500
        vendor_data = Vendor.query.get(session['vendor_id'])
        if not vendor_data:
            session.clear()
            return redirect(url_for('login'))
            
        # جلب المنتجات المربوطة بالمورد
        all_products = Product.query.filter_by(vendor_id=vendor_data.id).all()
        
        return render_template('dashboard.html', 
                               vendor=vendor_data, 
                               products=all_products)
    except Exception as e:
        print(f"Database Error: {e}")
        return "خطأ في تحميل اللوحة، تأكد من اتصال قاعدة البيانات", 500

# 5. وظائف المعالجة (Actions) - رفع المنتجات
@app.route('/upload_product', methods=['POST'])
def upload_product():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form.get('name')
    price = request.form.get('price')
    desc = request.form.get('description')
    
    if name and price:
        new_item = Product(name=name, price=float(price), description=desc, vendor_id=session['vendor_id'])
        db.session.add(new_item)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 6. تشغيل التطبيق (Runner)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
