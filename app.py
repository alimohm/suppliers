import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# 1. استيراد المحركات الأساسية من ملفاتك المنفصلة
from config import Config
from database import db, init_db
from models import AdminUser, Vendor, VendorStaff, Product, seed_system

# 2. استيراد المنطق (Logics) من الملفات الظاهرة في المجلد
from vendor_logic import login_vendor, is_logged_in
from admin_logic import verify_admin_credentials, is_admin_logged_in
# من الممكن استدعاء وظائف مالية من finance.py لاحقاً هنا

app = Flask(__name__)
app.config.from_object(Config)

# ربط وتهيئة قاعدة البيانات
init_db(app)

# --- [ منطقة حقن البيانات والسيادة ] ---
with app.app_context():
    db.create_all()  # إنشاء الجداول من models.py
    seed_system()   # حقن (علي محجوب) و (محجوب أونلاين) و (موظف تجريبي)

# --- [ بوابة التوجيه الذكي ] ---
@app.route('/')
def index():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('vendor_login'))

# --- [ مسارات الإدارة: علي محجوب ] ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        success, msg = verify_admin_credentials(u, p) # تستدعى من admin_logic.py
        if success:
            flash(msg, "success")
            return redirect(url_for('admin_dashboard'))
        flash(msg, "danger")
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in(): return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

# --- [ مسارات المورد: محجوب أونلاين ] ---
@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        success, msg = login_vendor(u, p) # تستدعى من vendor_logic.py
        if success:
            flash(msg, "success")
            return redirect(url_for('vendor_dashboard'))
        flash(msg, "danger")
    return render_template('vendor_login.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if not is_logged_in(): return redirect(url_for('vendor_login'))
    # جلب بيانات المورد لعرضها (الاسم بالعربي والعلامة التجارية)
    vendor = Vendor.query.get(session.get('user_id'))
    return render_template('dashboard.html', vendor=vendor)

# --- [ الخروج ] ---
@app.route('/logout')
def logout():
    session.clear()
    flash("تم تسجيل الخروج بنجاح.", "info")
    return redirect(url_for('vendor_login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
