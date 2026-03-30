import os
import requests  # تم التأكد من تضمينها لربط قمرة
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# مفتاح الأمان للجلسات
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_online_decentralized_2026')

# --- إعدادات الربط الذكي مع Railway والقاعدة ---
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

db = SQLAlchemy(app)

# --- مفتاح قمرة كلاود ---
QAMRAH_API_KEY = os.environ.get('QAMRAH_API_KEY')

# --- الهيكل الداخلي: جداول المنصة ---
class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100))
    brand_name = db.Column(db.String(100))
    wallet_address = db.Column(db.String(100), unique=True) # المحفظة اللامركزية

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    # الحالة: 'draft' (مسودة للمراجعة)
    status = db.Column(db.String(20), default='draft') 
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))

# --- تهيئة المنصة وحساب المؤسس ---
def init_db():
    with app.app_context():
        try:
            db.create_all()
            if not Vendor.query.filter_by(username='ali').first():
                # توليد محفظة رقمية فريدة للمؤسس
                new_wallet = "MQ-" + os.urandom(6).hex().upper()
                admin = Vendor(
                    username='ali',
                    password='123',
                    owner_name='علي محجوب',
                    brand_name='محجوب ستور',
                    wallet_address=new_wallet
                )
                db.session.add(admin)
                db.session.commit()
                print(f"✅ تم تأسيس العقدة الأولى. المحفظة: {new_wallet}")
        except Exception as e:
            print(f"⚠️ خطأ في القاعدة: {e}")

init_db()

# --- المسارات البرمجية (Routes) ---

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        vendor = Vendor.query.filter_by(username=u).first()
        
        # منطق التحقق المطلوب
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
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    
    # تمرير البيانات بشكل صحيح لتفادي خطأ 500
    vendor_products = Product.query.filter_by(vendor_id=session['vendor_id']).all()
    return render_template('dashboard.html', products=vendor_products)

@app.route('/upload_product', methods=['POST'])
def upload_product():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    
    # رفع المنتج كـ "مسودة" للمراجعة
    new_p = Product(
        name=request.form.get('name'),
        price=request.form.get('price'),
        vendor_id=session['vendor_id'],
        status='draft'
    )
    db.session.add(new_p)
    db.session.commit()
    
    flash("تم إرسال المنتج بنجاح. حالته الآن: مسودة قيد المراجعة.", "info")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
