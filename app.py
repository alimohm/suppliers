import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# مفتاح أمان للجلسات وتشفير البيانات
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_royal_purple_2026')

# --- 1. إعدادات قاعدة البيانات (Railway) ---
# التأكد من استخدام الرابط العام لضمان استقرار الاتصال
db_url = os.environ.get('DATABASE_URL')

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 2. النماذج (Models) مطابقة لجداولك الحقيقية ---
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100))   # لعرض 'الفقية للتجارة' أو 'علي محجوب'
    wallet_address = db.Column(db.String(100)) # لعرض رقم المحفظة

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))

# --- 3. المسارات (Routes) ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        # التحقق من البيانات المسجلة في جدول vendor
        vendor = Vendor.query.filter_by(username=u, password=p).first()
        
        if vendor:
            session['vendor_id'] = vendor.id
            return redirect(url_for('dashboard'))
        else:
            flash("خطأ في بيانات الدخول، يرجى المحاولة مرة أخرى")
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # التحقق من وجود جلسة نشطة للمورد
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # جلب بيانات المورد لإرسالها للقالب (layout)
        # هذا السطر هو المسؤول عن ظهور الاسم تحت اللوجو الأبيض
        vendor_data = Vendor.query.get(session['vendor_id'])
        
        if not vendor_data:
            session.clear()
            return redirect(url_for('login'))
            
        # جلب قائمة المنتجات الخاصة بالمورد فقط
        products_list = Product.query.filter_by(vendor_id=vendor_data.id).all()
        
        # تمرير 'vendor' ليعرض الاسم في الـ sidebar والـ dashboard
        return render_template('dashboard.html', 
                               vendor=vendor_data, 
                               products=products_list)
                               
    except Exception as e:
        # طباعة الخطأ في سجلات ريلوي للمتابعة
        print(f"حدث خطأ: {e}")
        return "خطأ في تحميل البيانات، يرجى التحقق من اتصال قاعدة البيانات", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- 4. بدء التشغيل ---
if __name__ == "__main__":
    # التشغيل على المنفذ المخصص من ريلوي
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
