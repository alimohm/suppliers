import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- 1. استدعاء المحركات والبيانات السيادية ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin
# استدعاء المنطق (Logic) من ملفك الذي جهزته
from logic import login_vendor_logic, verify_admin_credentials 

# --- 2. تعريف التطبيق (يجب أن يكون هنا لمنع خطأ NameError) ---
app = Flask(__name__)
app.config.from_object(Config)

# إعدادات الميديا والرفع
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- 3. تهيئة القاعدة وحل مشكلة الأعمدة المفقودة ---
init_db(app)

with app.app_context():
    # إنشاء الجداول وتحديثها لضمان وجود أعمدة (status, wallet_address)
    db.create_all() 
    # حقن بيانات الهوية (علي محجوب)
    seed_admin() 

# --- 4. توابع التحقق من الجلسات (Security) ---
def is_logged_in():
    return session.get('role') == 'vendor' and 'user_id' in session

def is_admin_logged_in():
    return session.get('role') == 'admin' and 'admin_id' in session

# ==========================================
# --- 5. المسارات وبوابات تسجيل الدخول ---
# ==========================================

# [توجيه الصفحة الرئيسية]
@app.route('/')
def home_redirect():
    if is_admin_logged_in(): 
        return redirect(url_for('admin_dashboard_route'))
    if is_logged_in(): 
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

# [بوابة دخول المورد]
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # استخدام .strip() لضمان دقة البيانات المدخلة
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        # استدعاء المنطق الجاهز من ملف logic.py
        success, message = login_vendor_logic(u, p)
        
        if success:
            flash(message, "success")
            return redirect(url_for('dashboard'))
        else:
            flash(message, "danger")
            
    return render_template('login.html')

# [لوحة تحكم المورد]
@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    
    vendor_data = Vendor.query.get(session.get('user_id'))
    products_list = Product.query.filter_by(vendor_id=vendor_data.id).all()
    return render_template('dashboard.html', vendor=vendor_data, products=products_list)

# [بوابة دخول الإدارة - برج المراقبة]
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    
    if request.method == 'POST':
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        
        # استخدام منطق التحقق الإداري المستدعى
        success, message = verify_admin_credentials(u, p)
        
        if success:
            flash("مرحباً بك في برج المراقبة.", "success")
            return redirect(url_for('admin_dashboard_route'))
        else:
            flash(message, "danger")
            
    return render_template('admin_login.html')

# [لوحة تحكم الإدارة]
@app.route('/admin/dashboard')
def admin_dashboard_route():
    if not is_admin_logged_in(): return redirect(url_for('admin_login_route'))
    
    all_vendors = Vendor.query.all()
    return render_template('admin_dashboard.html', vendors=all_vendors)

# [تأمين الخروج والمسح الكامل للجلسة]
@app.route('/logout')
def logout_route():
    session.clear() # مسح شامل لمنع الاختراق
    flash("تم تأمين البوابات بنجاح.", "info")
    return redirect(url_for('login_page'))

# --- 6. تشغيل المحرك على Railway ---
if __name__ == '__main__':
    # تشغيل المنفذ 8080 المعتمد للسيرفرات السحابية
    app.run(host='0.0.0.0', port=8080, debug=True)
