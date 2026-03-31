import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# مفتاح الأمان للجلسات
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_2026_key')

# --- 1. إعداد قاعدة البيانات ---
# يسحب الرابط من DATABASE_URL الذي وضعناه في Railway
db_url = os.environ.get('DATABASE_URL')

# معالجة الرابط ليتوافق مع SQLAlchemy
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 2. تعريف الجداول (مطابق لبياناتك الحقيقية) ---
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100))   # 'علي محجوب' في صورتك
    wallet_address = db.Column(db.String(100)) # 'MQ-5035D99C' في صورتك

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))

# --- 3. مسارات التطبيق (Routes) ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        # البحث في الجدول عن المستخدم وكلمة المرور
        vendor = Vendor.query.filter_by(username=u, password=p).first()
        
        if vendor:
            # تخزين ID المورد في الجلسة (رقم 1 في صورتك)
            session['vendor_id'] = vendor.id
            return redirect(url_for('dashboard'))
        else:
            flash("اسم المستخدم أو كلمة المرور غير صحيحة")
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # التأكد من تسجيل الدخول
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # جلب بيانات المورد بناءً على ID الجلسة
        vendor_data = Vendor.query.get(session['vendor_id'])
        
        if not vendor_data:
            session.clear()
            return redirect(url_for('login'))
            
        # جلب المنتجات المربوطة بهذا المورد
        products_list = Product.query.filter_by(vendor_id=vendor_data.id).all()
        
        # عرض صفحة الداشبورد ودمجها مع الهيكل layout.html
        return render_template('dashboard.html', 
                               vendor=vendor_data, 
                               products=products_list)
                               
    except Exception as e:
        # يطبع الخطأ في سجلات ريلوي للمتابعة
        print(f"Database Error: {e}")
        return f"خطأ في الاتصال بقاعدة البيانات: {str(e)}", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- 4. تشغيل التطبيق ---
if __name__ == "__main__":
    # استخدام المنفذ 8080 كما يطلبه Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
