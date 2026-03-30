import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# مفتاح سري قوي للجلسات
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_online_private_key_2026')

# --- إعدادات قاعدة البيانات (Railway) ---
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

db = SQLAlchemy(app)

# --- مفتاح قمرة كلاود (المسحوب من المتغيرات) ---
QAMRAH_API_KEY = os.environ.get('QAMRAH_API_KEY')

# --- الهيكل الداخلي: جدول الموردين ---
class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    brand_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    # الهوية اللامركزية: المحفظة الرقمية
    wallet_address = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# --- الهيكل الداخلي: جدول المنتجات ---
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    # الحالة: pending (قيد المراجعة), approved (تم النشر), rejected (مرفوض)
    status = db.Column(db.String(20), default='pending') 
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# --- تهيئة المنصة وحساب المؤسس ---
def init_platform():
    with app.app_context():
        try:
            db.create_all()
            if not Vendor.query.filter_by(username='ali').first():
                # توليد عنوان محفظة رقمية تلقائي فريد
                random_wallet = "MQ-" + os.urandom(6).hex().upper()
                admin = Vendor(
                    username='ali',
                    password='123',
                    owner_name='علي محجوب',
                    brand_name='محجوب ستور',
                    phone_number='777777777',
                    email='admin@mahjoub.online',
                    wallet_address=random_wallet
                )
                db.session.add(admin)
                db.session.commit()
                print(f"✅ تم تفعيل الهوية اللامركزية. المحفظة: {random_wallet}")
        except Exception as e:
            print(f"⚠️ خطأ في التهيئة: {e}")

init_platform()

# --- المسارات (Routes) ---

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        vendor = Vendor.query.filter_by(username=u).first()
        
        if not vendor:
            flash("عذراً، هذا المورد غير مسجل في المنصة اللامركزية.", "danger")
        elif vendor.password != p:
            flash("كلمة المرور غير صحيحة، تأكد وحاول مجدداً.", "warning")
        else:
            session.update({
                'vendor_id': vendor.id,
                'vendor_name': vendor.owner_name,
                'brand_name': vendor.brand_name,
                'wallet': vendor.wallet_address
            })
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session: return redirect(url_for('login'))
    # جلب منتجات المورد الحالية
    my_products = Product.query.filter_by(vendor_id=session['vendor_id']).all()
    return render_template('dashboard.html', products=my_products)

@app.route('/upload_product', methods=['POST'])
def upload_product():
    if 'vendor_id' not in session: return redirect(url_for('login'))
    
    name = request.form.get('name')
    price = request.form.get('price')
    desc = request.form.get('description')
    
    new_p = Product(
        name=name,
        price=price,
        description=desc,
        vendor_id=session['vendor_id'],
        status='pending' # المنطق المطلوب: يظهر قيد المراجعة فوراً
    )
    db.session.add(new_p)
    db.session.commit()
    
    flash("تم إرسال المنتج بنجاح. الحالة الحالية: قيد المراجعة من الإدارة.", "info")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
