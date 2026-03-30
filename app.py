import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "mahjoub_online_private_key_2026"

# الربط الديناميكي مع DATABASE_URL الموضح في صورتك
# ملاحظة: Railway يضيف هذا المتغير تلقائياً للسيرفر
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- جدول الموردين الشامل (الهيكل الجديد) ---
class Vendor(db.Model):
    __tablename__ = 'vendors'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # بيانات الدخول
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    # البيانات التعريفية التي طلبتها
    owner_name = db.Column(db.String(100), nullable=False)   # اسم المالك
    brand_name = db.Column(db.String(100), nullable=False)   # اسم العلامة التجارية
    phone_number = db.Column(db.String(20), nullable=False)  # رقم الهاتف
    email = db.Column(db.String(120), unique=True, nullable=False) # البريد
    address = db.Column(db.String(255), nullable=True)       # العنوان
    
    # التوثيق والحالة
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# --- أمر إنشاء الجداول تلقائياً ---
with app.app_context():
    db.create_all()
    print("✅ تم الربط بنجاح وبناء الجداول في Postgres Railway!")

# --- مسار تسجيل الدخول (بنظام الحوكمة) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_in = request.form.get('username').strip()
        pass_in = request.form.get('password').strip()
        
        vendor = Vendor.query.filter_by(username=user_in).first()
        
        if not vendor:
            flash("عذراً، هذا المورد غير مسجل في المنصة اللامركزية.", "danger")
        elif vendor.password != pass_in:
            flash("كلمة المرور غير صحيحة، تأكد وحاول مجدداً.", "warning")
        else:
            session['vendor_id'] = vendor.id
            session['vendor_name'] = vendor.owner_name
            return redirect(url_for('dashboard'))
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    return f"مرحباً بك يا {session['vendor_name']} في لوحة تحكم محجوب أونلاين"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
