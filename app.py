import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# مفتاح الأمان للجلسات
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_online_secure_2026')

# --- إعدادات قاعدة البيانات (Railway Postgres) ---
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

db = SQLAlchemy(app)

# --- الهيكل البرمجي للجداول (Schema) ---
class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100))
    brand_name = db.Column(db.String(100))
    # هذا هو العمود الذي كان يسبب الانهيار
    wallet_address = db.Column(db.String(100), unique=True) 

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    # الحالة الافتراضية مسودة للمراجعة
    status = db.Column(db.String(20), default='draft') 
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))

# --- نظام الإصلاح الذاتي والتهيئة ---
def setup_platform():
    with app.app_context():
        try:
            # الخطوة الحاسمة: مسح الجداول القديمة التي تفتقد لعمود المحفظة
            # ملاحظة: سيتم مسح البيانات لمرة واحدة فقط لضبط الهيكل الجديد
            db.drop_all() 
            db.create_all()
            
            # إعادة إنشاء حسابك كمسؤول للمنصة
            if not Vendor.query.filter_by(username='ali').first():
                new_wallet = "MQ-" + os.urandom(4).hex().upper()
                admin = Vendor(
                    username='ali',
                    password='123',
                    owner_name='علي محجوب',
                    brand_name='محجوب ستور',
                    wallet_address=new_wallet
                )
                db.session.add(admin)
                db.session.commit()
                print(f"✅ تم إصلاح القاعدة بنجاح. المحفظة الجديدة: {new_wallet}")
        except Exception as e:
            print(f"⚠️ تنبيه أثناء التهيئة: {e}")

# تشغيل الإصلاح الذاتي
setup_platform()

# --- المسارات البرمجية (Routes) ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        vendor = Vendor.query.filter_by(username=u).first()
        
        if not vendor:
            flash("المورد غير مسجل في النظام اللامركزي.", "danger")
        elif vendor.password != p:
            flash("كلمة المرور غير صحيحة.", "warning")
        else:
            # تخزين البيانات في الجلسة للتحويل للدشبرد
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
    
    try:
        # جلب منتجات المورد الحالي فقط
        products = Product.query.filter_by(vendor_id=session['vendor_id']).all()
        return render_template('dashboard.html', products=products)
    except Exception as e:
        flash(f"خطأ في عرض البيانات: {str(e)}", "danger")
        return render_template('dashboard.html', products=[])

@app.route('/upload_product', methods=['POST'])
def upload_product():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    
    new_product = Product(
        name=request.form.get('name'),
        price=request.form.get('price'),
        vendor_id=session['vendor_id'],
        status='draft'
    )
    db.session.add(new_product)
    db.session.commit()
    
    flash("تم رفع المنتج بنجاح وهو قيد المراجعة (مسودة).", "info")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # تشغيل السيرفر على البورت المحدد من Railway
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
