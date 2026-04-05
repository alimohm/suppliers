import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استدعاء المنطق البرمجي
from vendor_logic import login_vendor 
from admin_logic import (
    verify_admin_credentials, 
    get_admin_stats,
    approve_vendor_logic,
    get_dashboard_data
)

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات
init_db(app)

# ✅ الحل البديل لـ before_first_request: استخدام وظيفة التهيئة اليدوية
def startup_setup():
    with app.app_context():
        try:
            db.create_all()
            # زرع بيانات المالك (علي محجوب)
            models.seed_initial_data()
            print("✅ نظام محجوب أونلاين: السيادة التقنية جاهزة.")
        except Exception as e:
            print(f"❌ خطأ في تهيئة النظام: {e}")

# تنفيذ التهيئة عند تشغيل الملف
startup_setup()

# --- [ المسارات ] ---

@app.route('/')
def index():
    role = session.get('role')
    if role == 'super_admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('role') == 'super_admin':
        return redirect(url_for('admin_dashboard'))

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
    return render_template('admin_main.html', username=session.get('username'), stats=stats)

@app.route('/admin/vendors-accreditation')
def vendors_accreditation():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    all_vendors = get_dashboard_data()
    stats = get_admin_stats()
    
    return render_template('admin_accounts.html', 
                           username=session.get('username'),
                           vendors=all_vendors, 
                           pending_count=stats.get('pending', 0))

@app.route('/admin/approve/<int:vendor_id>', methods=['POST'])
def approve_vendor(vendor_id):
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    success, msg = approve_vendor_logic(vendor_id)
    flash(msg, "success" if success else "danger")
    return redirect(url_for('vendors_accreditation'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
