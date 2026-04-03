import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- 1. الاستيراد من ملفاتك المستقلة (بدون تكرار) ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin
from logic import login_vendor, is_logged_in
from admin_logic import verify_admin_credentials, is_admin_logged_in

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات الميديا
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# تفعيل القاعدة
init_db(app)
with app.app_context():
    db.create_all()
    seed_admin()

# ==========================================
# --- 2. بوابات الدخول (توجيه فقط) ---
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    if request.method == 'POST':
        u, p = request.form.get('username'), request.form.get('password')
        
        # استدعاء المنطق السيادي من logic.py
        success, message = login_vendor(u, p) 
        if success:
            return redirect(url_for('dashboard'))
        flash(message, "danger") # رسائل: موقف، مقيد، تحت المراجعة
    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    if request.method == 'POST':
        u, p = request.form.get('admin_user'), request.form.get('admin_pass')
        
        # استدعاء منطق برج المراقبة من admin_logic.py
        success, message = verify_admin_credentials(u, p)
        if success:
            return redirect(url_for('admin_dashboard_route'))
        flash(message, "danger")
    return render_template('admin_login.html')

# ==========================================
# --- 3. مسارات المورد (Dashboard) ---
# ==========================================
@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    vendor_data = Vendor.query.filter_by(username=session.get('username')).first()
    products_list = Product.query.filter_by(brand=vendor_data.brand_name).all()
    return render_template('dashboard.html', vendor=vendor_data, products=products_list)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in(): return redirect(url_for('login_page'))
    # ... كود الرفع الخاص بك ...
    return render_template('add_product.html')

# ==========================================
# --- 4. مسارات الإدارة (برج المراقبة) ---
# ==========================================
@app.route('/admin/dashboard')
def admin_dashboard_route():
    if not is_admin_logged_in(): return redirect(url_for('admin_login_route'))
    all_vendors = Vendor.query.all()
    pending_items = Product.query.filter_by(status='pending').all()
    return render_template('admin_dashboard.html', vendors=all_vendors, pending_items=pending_items)

# ==========================================
# --- 5. التحكم بالخروج ---
# ==========================================
@app.route('/logout')
def logout_route():
    session.clear()
    flash("تم تأمين البوابات والخروج بنجاح.", "info")
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
