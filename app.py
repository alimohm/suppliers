import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# مفتاح أمان لضمان استقرار الجلسات ومنع الانهيار
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_online_2026_secure')

# --- إعداد الاتصال بقاعدة بيانات Railway ---
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- تعريف النماذج (Models) بأسماء الجداول المفردة ---
class Vendor(db.Model):
    __tablename__ = 'vendor' # مطابقة لاسم الجدول في Railway
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100))
    wallet_address = db.Column(db.String(100))

class Product(db.Model):
    __tablename__ = 'product' # مطابقة لاسم الجدول في Railway
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))

# --- المسارات (Routes) ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        # البحث عن المورد في القاعدة
        vendor = Vendor.query.filter_by(username=u, password=p).first()
        if vendor:
            session['vendor_id'] = vendor.id
            return redirect(url_for('dashboard'))
        flash("بيانات الدخول غير صحيحة")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # جلب بيانات المورد الحالي بأمان
        vendor_data = Vendor.query.get(session['vendor_id'])
        
        if not vendor_data:
            session.clear()
            return redirect(url_for('login'))
            
        # جلب المنتجات المربوطة بهذا المورد
        products_list = Product.query.filter_by(vendor_id=vendor_data.id).all()
        
        # تمرير المتغيرات للقالب المقسم (layout + dashboard)
        return render_template('dashboard.html', 
                               vendor=vendor_data, 
                               products=products_list)
    except Exception as e:
        # معالجة الخطأ الذي ظهر في صورتك الأخيرة
        print(f"Database Error: {e}")
        return "خطأ في تحميل اللوحة، تأكد من اتصال قاعدة البيانات والروابط", 500

@app.route('/upload_product', methods=['POST'])
def upload_product():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    
    if name and price:
        try:
            new_product = Product(
                name=name, 
                price=float(price), 
                description=description, 
                vendor_id=session['vendor_id']
            )
            db.session.add(new_product)
            db.session.commit()
            flash("تم رفع المنتج بنجاح")
        except Exception as e:
            db.session.rollback()
            print(f"Upload Error: {e}")
            
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- تشغيل التطبيق ---
if __name__ == "__main__":
    # المنفذ 8080 كما يظهر في سجلات Railway الخاصة بك
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
