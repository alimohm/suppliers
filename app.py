import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- استيراد ملفات المشروع ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin
from logic import login_vendor, is_logged_in
from admin_logic import is_admin_logged_in, verify_admin_credentials, logout_admin_logic

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات الرفع والميديا
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# تفعيل قاعدة البيانات وسياق التطبيق
init_db(app)
with app.app_context():
    db.create_all()
    seed_admin() # التأكد من وجود حساب الإدارة "صبري"

# ==========================================
# --- مسار لوحة المورد (Dashboard) ---
# ==========================================
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # 1. إذا كان المورد مسجل دخوله مسبقاً
    if is_logged_in():
        vendor = Vendor.query.filter_by(username=session['username']).first()
        my_products = Product.query.filter_by(brand=vendor.brand_name).all()
        return render_template('dashboard.html', vendor=vendor, products=my_products, show_welcome=False)

    # 2. معالجة محاولة تسجيل الدخول للمورد
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if login_vendor(u, p):
            vendor = Vendor.query.filter_by(username=session['username']).first()
            my_products = Product.query.filter_by(brand=vendor.brand_name).all()
            # الدخول بنجاح -> عرض اللوحة مع رسالة ترحيب
            return render_template('dashboard.html', vendor=vendor, products=my_products, show_welcome=True)
            
    return render_template('login.html')

# ==========================================
# --- مسار لوحة الإدارة (Admin Dashboard) ---
# ==========================================
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard_route():
    # 1. إذا كان المدير (صبري) مسجل دخوله مسبقاً
    if is_admin_logged_in():
        all_vendors = Vendor.query.all()
        pending_items = Product.query.filter_by(status='pending').all()
        return render_template('admin_dashboard.html', 
                               vendors=all_vendors, 
                               pending_count=len(pending_items),
                               pending_items=pending_items, 
                               show_welcome=False)

    # 2. معالجة محاولة تسجيل الدخول للمدير
    if request.method == 'POST':
        u = request.form.get('admin_user')
        p = request.form.get('admin_pass')
        if verify_admin_credentials(u, p):
            all_vendors = Vendor.query.all()
            pending_items = Product.query.filter_by(status='pending').all()
            # الدخول بنجاح -> عرض برج المراقبة مع رسالة الترحيب الملكية
            return render_template('admin_dashboard.html', 
                                   vendors=all_vendors, 
                                   pending_count=len(pending_items),
                                   pending_items=pending_items, 
                                   show_welcome=True)
            
    return render_template('admin_login.html')

# ==========================================
# --- عمليات النظام (Logout & Actions) ---
# ==========================================

@app.route('/logout')
def logout_route():
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
