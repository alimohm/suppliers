import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- 1. استيراد المحركات المركزية والمنطق السيادي ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin
from logic import login_vendor, is_logged_in
from admin_logic import verify_admin_credentials, is_admin_logged_in

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات الميديا وتأمين مسار الرفع
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- 2. تفعيل قاعدة البيانات وحقن الهوية الرقمية ---
# ملاحظة: init_db تقوم باستدعاء create_all لتحديث الجداول في Railway
init_db(app)

with app.app_context():
    # استدعاء seed_admin لضمان وجود حساباتك مشفرة بكلمة 123
    seed_admin() 

# ==========================================
# --- 3. بوابة دخول المورد (المنصة اللامركزية) ---
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # منع الدخول المزدوج
    if is_logged_in(): return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # تنظيف المدخلات من المسافات لضمان دقة المطابقة
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        if not u or not p:
            flash("يرجى إدخال اسم المستخدم وكلمة المرور لتأمين الدخول.", "warning")
            return redirect(url_for('login_page'))

        # استدعاء المنطق الذكي الذي يميز بين (المستخدم غير موجود) و (كلمة المرور خطأ)
        success, message = login_vendor(u, p)
        
        if success:
            flash(message, "success")
            return redirect(url_for('dashboard'))
        else:
            # هنا ستظهر رسالة "غير مسجل" أو "كلمة مرور خطأ" بناءً على منطق logic.py
            flash(message, "danger")
            
    return render_template('login.html')

# ==========================================
# --- 4. بوابة دخول الإدارة (برج المراقبة) ---
# ==========================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    
    if request.method == 'POST':
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        
        success, message = verify_admin_credentials(u, p)
        
        if success:
            flash("مرحباً بك يا سيد علي في برج المراقبة.", "success")
            return redirect(url_for('admin_dashboard_route'))
        else:
            flash(message, "danger")
            
    return render_template('admin_login.html')

# ==========================================
# --- 5. مسارات المورد (لوحة التحكم السيادية) ---
# ==========================================
@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    
    vendor_data = Vendor.query.filter_by(username=session.get('username')).first()
    if not vendor_data:
        session.clear()
        return redirect(url_for('login_page'))
        
    products_list = Product.query.filter_by(vendor_id=vendor_data.id).all()
    return render_template('dashboard.html', vendor=vendor_data, products=products_list)

# ==========================================
# --- 6. مسارات الإدارة (التحكم في الموردين) ---
# ==========================================
@app.route('/admin/dashboard')
def admin_dashboard_route():
    if not is_admin_logged_in(): return redirect(url_for('admin_login_route'))
    
    all_vendors = Vendor.query.all()
    pending_items = Product.query.filter_by(status='pending').all()
    
    return render_template('admin_dashboard.html', 
                           vendors=all_vendors, 
                           pending_items=pending_items)

# ==========================================
# --- 7. التحكم النهائي وتأمين الخروج ---
# ==========================================
@app.route('/')
def home_redirect():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    if is_logged_in(): return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout_route():
    session.clear()
    flash("تم تأمين البوابات بنجاح. في أمان الله.", "info")
    return redirect(url_for('login_page'))

# --- تشغيل المحرك ---
if __name__ == '__main__':
    # التشغيل على المنفذ 8080 المعتمد لخدمات Railway
    app.run(host='0.0.0.0', port=8080, debug=True)
