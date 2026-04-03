import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- 1. استيراد الإعدادات والمنطق من ملفاتك المستقلة ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin
from logic import login_vendor, is_logged_in
from admin_logic import verify_admin_credentials, is_admin_logged_in

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات الميديا ورفع الملفات
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- 2. تفعيل قاعدة البيانات وحقن الهوية التشغيلية ---
init_db(app)
with app.app_context():
    db.create_all()
    seed_admin() 

# ==========================================
# --- 3. بوابة دخول المورد (سوقك الذكي) ---
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # استخدام strip() لإزالة أي مسافات زائدة قد تسبب خطأ في كلمة المرور
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        if not u or not p:
            flash("يرجى إدخال اسم المستخدم وكلمة المرور.", "warning")
            return redirect(url_for('login_page'))

        # استدعاء المنطق من logic.py
        success, message = login_vendor(u, p)
        
        if success:
            if "تنبيه" in message: flash(message, "warning")
            return redirect(url_for('dashboard'))
        else:
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
        
        # استدعاء منطق الإدارة من admin_logic.py
        success, message = verify_admin_credentials(u, p)
        
        if success:
            return redirect(url_for('admin_dashboard_route'))
        else:
            flash(message, "danger")
            
    return render_template('admin_login.html')

# ==========================================
# --- 5. مسارات المورد ---
# ==========================================
@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    
    vendor_data = Vendor.query.filter_by(username=session.get('username')).first()
    if not vendor_data:
        session.clear()
        return redirect(url_for('login_page'))
        
    products_list = Product.query.filter_by(brand=vendor_data.brand_name).all()
    return render_template('dashboard.html', vendor=vendor_data, products=products_list)

# ==========================================
# --- 6. مسارات الإدارة ---
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
