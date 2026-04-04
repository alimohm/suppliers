import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# 1. استيراد الإعدادات والموديلات
from config import Config
from database import db, init_db
from models import Vendor, AdminUser, Product, seed_admin

# 2. استيراد منطق التحقق (Logic)
# تأكد أن verify_admin_credentials و login_vendor تعيد (True, "رسالة نجاح") عند المطابقة
from logic import login_vendor, is_logged_in
from admin_logic import verify_admin_credentials, is_admin_logged_in

app = Flask(__name__)
app.config.from_object(Config)

# ربط قاعدة البيانات (Postgres أو SQLite حسب الإعدادات)
init_db(app)

# 3. تهيئة الجداول وحقن البيانات (علي محجوب / محجوب أونلاين) فور التشغيل
with app.app_context():
    db.create_all() 
    seed_admin() # إنشاء الحسابات إذا لم تكن موجودة

# --- [ البوابات والروابط الرئيسية ] ---

@app.route('/')
def index():
    # توجيه ذكي: إذا كان مسجلاً كمسؤول يذهب للوحة الإدارة، وإذا كان مورداً يذهب للوحته
    if is_admin_logged_in(): 
        return redirect(url_for('admin_dashboard'))
    if is_logged_in(): 
        return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('login_page'))

# 📦 بوابة دخول الموردين (محجوب أونلاين)
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): 
        return redirect(url_for('vendor_dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        success, msg = login_vendor(u, p)
        if success:
            # تم تسجيل الدخول بنجاح، استدعاء لوحة التحكم فوراً
            flash(msg, "success")
            return redirect(url_for('vendor_dashboard'))
        else:
            flash(msg, "danger")
            
    return render_template('login.html')

# 🏛️ بوابة دخول الإدارة (علي محجوب)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in(): 
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # استخدام الأسماء البرمجية الموحدة لحقول الإدارة
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        
        success, msg = verify_admin_credentials(u, p)
        if success:
            # التحقق نجح، التوجه للداشبورد الخاص بالإدارة
            flash(msg, "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash(msg, "danger")
            
    return render_template('admin_login.html')

# --- [ لوحات التحكم - Dashboards ] ---

# 1. لوحة تحكم المورد (Vendor Dashboard)
@app.route('/dashboard')
def vendor_dashboard():
    if not is_logged_in(): 
        flash("يرجى تسجيل الدخول أولاً كـ مورد", "warning")
        return redirect(url_for('login_page'))
    
    # جلب بيانات المورد الحالي من قاعدة البيانات
    vendor_id = session.get('user_id')
    current_vendor = Vendor.query.get(vendor_id)
    
    # جلب منتجات هذا المورد فقط
    vendor_products = Product.query.filter_by(vendor_id=vendor_id).all()
    
    return render_template('dashboard.html', vendor=current_vendor, products=vendor_products)

# 2. لوحة تحكم الإدارة (Admin Dashboard)
@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in(): 
        flash("هذه المنطقة مخصصة للإدارة فقط", "danger")
        return redirect(url_for('admin_login'))
    
    # هنا يمكن جلب إحصائيات عامة للمسؤول (عدد الموردين، عدد المنتجات المعلقة)
    all_vendors = Vendor.query.all()
    pending_products = Product.query.filter_by(status='pending').all()
    
    return render_template('admin_dashboard.html', vendors=all_vendors, pending=pending_products)

# --- [ الخروج ] ---

@app.route('/logout')
def logout():
    session.clear()
    flash("تم تسجيل الخروج وتأمين الجلسة.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
