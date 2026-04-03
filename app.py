import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- 1. تعريف التطبيق فوراً (للقضاء على NameError) ---
app = Flask(__name__) #

# --- 2. استيراد المحركات بعد تعريف الـ app ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin

# استيراد المنطق من ملفاتك الحالية
from logic import login_vendor, is_logged_in # للموردين
from admin_logic import is_admin_logged_in, verify_admin_credentials # للإدارة

app.config.from_object(Config)

# إعدادات الميديا والرفع
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# تهيئة القاعدة وتحديث الجداول
init_db(app)

with app.app_context():
    # حل مشكلة الأعمدة المفقودة (status, wallet_address)
    db.create_all() 
    # حقن بيانات الإدارة (علي محجوب)
    seed_admin() 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==========================================
# --- مسارات الموردين (Vendors) ---
# ==========================================

@app.route('/')
def index():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    if is_logged_in(): return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        # استخدام دالتك في logic.py
        success, message = login_vendor(u, p) 
        if success:
            flash(message, "success")
            return redirect(url_for('dashboard'))
        flash(message, "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    vendor_data = Vendor.query.get(session.get('user_id'))
    if not vendor_data: return redirect(url_for('logout_route'))
    products_list = Product.query.filter_by(vendor_id=vendor_data.id).all()
    return render_template('dashboard.html', vendor=vendor_data, products=products_list)

# ==========================================
# --- مسارات الإدارة المركزية (Admin) ---
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    if request.method == 'POST':
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        
        # استخدام دالتك في admin_logic.py
        success, message = verify_admin_credentials(u, p)
        if success:
            flash(message, "success")
            return redirect(url_for('admin_dashboard_route'))
        flash(message, "danger")
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard_route():
    if not is_admin_logged_in(): return redirect(url_for('admin_login_route'))
    all_vendors = Vendor.query.all()
    pending_products = Product.query.filter_by(status='pending').all()
    return render_template('admin_dashboard.html', 
                           vendors=all_vendors, 
                           pending_count=len(pending_products))

# --- تسجيل الخروج ---
@app.route('/logout')
def logout_route():
    session.clear() # تنظيف شامل للجلسة
    flash("تم تأمين النظام والخروج بنجاح.", "info")
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    # التوافق مع منفذ Railway الديناميكي
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
