import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models
from admin_logic import (
    verify_admin_credentials, 
    get_admin_stats, 
    approve_vendor_logic, 
    get_dashboard_data
)

app = Flask(__name__)
app.config.from_object(Config)

# 1. تهيئة قاعدة البيانات Postgres
init_db(app)

# 2. بناء الجداول وتأمين حساب القائد عند التشغيل
with app.app_context():
    db.create_all()
    models.seed_initial_data()

# --- [ بوابة الدخول الرئيسية ] ---

@app.route('/')
def index():
    if session.get('role') == 'super_admin':
        return redirect(url_for('admin_dashboard'))
    elif session.get('role') == 'vendor':
        return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('admin_login'))

# --- [ قسم الإدارة العليا ] ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        ok, msg = verify_admin_credentials(u, p)
        if ok:
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
    pending = get_admin_stats().get('pending', 0)
    return render_template('admin_accounts.html', 
                           vendors=vendors, 
                           pending_count=pending,
                           username=session.get('username'))

@app.route('/admin/add-vendor')
def admin_add_vendor():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    return render_template('admin_add_vendor.html')

@app.route('/admin/add-vendor/post', methods=['POST'])
def admin_add_vendor_post():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    brand = request.form.get('brand_name')
    user = request.form.get('username')
    pw = request.form.get('password')
    
    # إضافة المورد وتفعيله فوراً
    new_v = models.Vendor(brand_name=brand, username=user, password=pw, is_active=True)
    db.session.add(new_v)
    db.session.commit()
    
    # إنشاء المحفظة MAH تلقائياً للمورد الجديد
    wallet_no = f"MAH-{random.randint(1000, 9999)}"
    db.session.add(models.Wallet(wallet_number=wallet_no, vendor_id=new_v.id))
    db.session.commit()
    
    flash(f"تم إضافة {brand} وتفعيل هويته المالية بنجاح.", "success")
    return redirect(url_for('vendors_accreditation'))

@app.route('/admin/approve/<int:vendor_id>', methods=['POST'])
def approve_vendor(vendor_id):
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    success, msg = approve_vendor_logic(vendor_id)
    flash(msg, "success" if success else "danger")
    return redirect(url_for('vendors_accreditation'))

# --- [ بوابة الموردين ] ---

@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        vendor = models.Vendor.query.filter_by(username=u, password=p).first()
        
        if vendor:
            if vendor.is_active:
                session['vendor_id'] = vendor.id
                session['username'] = vendor.username
                session['role'] = 'vendor'
                return redirect(url_for('vendor_dashboard'))
            else:
                flash("حسابك قيد المراجعة، يرجى انتظار تفعيل الإدارة العليا.", "warning")
        else:
            flash("اسم المستخدم أو كلمة المرور غير صحيحة.", "danger")
    return render_template('login_vendor.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if session.get('role') != 'vendor':
        return redirect(url_for('vendor_login'))
    vendor = models.Vendor.query.get(session.get('vendor_id'))
    return render_template('vendor_dashboard.html', vendor=vendor)

# --- [ نظام الخروج ] ---

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# دالة التشغيل توضع في نهاية الملف دائماً
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
