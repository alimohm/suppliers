import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استدعاء المنطق البرمجي (Logic) لربط العقل بالجسد
from admin_logic import (
    verify_admin_credentials, 
    get_admin_stats, 
    approve_vendor_logic, 
    get_dashboard_data
)

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات (Postgres)
init_db(app)

# تهيئة النظام عند الإقلاع (تجاوز خطأ Flask 3)
def startup_setup():
    with app.app_context():
        try:
            db.create_all()
            models.seed_initial_data()
            print("✅ محجوب أونلاين: تم بناء الجداول وتأمين السيادة.")
        except Exception as e:
            print(f"❌ خطأ في التهيئة: {e}")

startup_setup()

# --- [ 1. التوجيه الرئيسي ] ---

@app.route('/')
def index():
    if session.get('role') == 'super_admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_login'))

# --- [ 2. بوابة الإدارة - Super Admin (علي محجوب) ] ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        success, msg = verify_admin_credentials(u, p)
        if success:
            session.permanent = True
            session['username'] = u
            session['role'] = 'super_admin'
            return redirect(url_for('admin_dashboard'))
        flash(msg, "danger")
    return render_template('login_admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    stats = get_admin_stats()
    return render_template('admin_main.html', 
                           username=session.get('username'), 
                           stats=stats)

@app.route('/admin/vendors-accreditation')
def vendors_accreditation():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    vendors = get_dashboard_data()
    stats = get_admin_stats()
    return render_template('admin_accounts.html', 
                           vendors=vendors, 
                           pending_count=stats['pending'],
                           username=session.get('username'))

@app.route('/admin/approve/<int:vendor_id>', methods=['POST'])
def approve_vendor(vendor_id):
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    success, msg = approve_vendor_logic(vendor_id)
    flash(msg, "success" if success else "danger")
    return redirect(url_for('vendors_accreditation'))

# --- [ 3. بوابة الموردين والمنتجات ] ---

@app.route('/vendor/dashboard')
def vendor_dashboard():
    # سيتم ربطه بـ vendor_logic لاحقاً عند بناء واجهة المورد
    if not session.get('username'):
        return redirect(url_for('index'))
    return render_template('vendor_dashboard.html')

@app.route('/vendor/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        # منطق إضافة منتج جديد لقاعدة البيانات
        pass
    return render_template('vendor_add_product.html')

# --- [ 4. الخروج ] ---

@app.route('/logout')
def logout():
    session.clear()
    flash("تم تسجيل الخروج بنجاح.", "info")
    return redirect(url_for('admin_login'))

# تشغيل السيرفر على منفذ Railway
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
