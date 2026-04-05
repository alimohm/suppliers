import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استدعاء المنطق البرمجي بدقة
from vendor_logic import login_vendor 
from admin_logic import (
    verify_admin_credentials, 
    manage_accounts_logic, 
    create_vendor_logic, 
    get_admin_stats,
    approve_vendor_logic,
    get_dashboard_data
)

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات - السيادة التقنية لمتجر محجوب
init_db(app)

@app.before_first_request
def setup_system():
    try:
        db.create_all()
        # زرع بيانات المالك (علي محجوب) كجذر للنظام
        models.seed_initial_data()
        print("✅ نظام محجوب أونلاين: الترددات جاهزة وقاعدة البيانات متصلة.")
    except Exception as e:
        print(f"❌ خطأ في تهيئة النظام: {e}")

# --- [ بوابة التوجيه الرئيسي ] ---

@app.route('/')
def index():
    role = session.get('role')
    if role == 'super_admin':
        return redirect(url_for('admin_dashboard'))
    elif role in ['vendor', 'staff']:
        return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('admin_login'))

# --- [ بوابة الإدارة - Super Admin (علي محجوب) ] ---

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
            flash(msg, "success")
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

# المسار الذي كان يسبب المشكلة (تم ربطه بـ admin_accounts.html)
@app.route('/admin/vendors-accreditation')
def vendors_accreditation():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    # جلب قائمة الموردين والبيانات
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

# --- [ بوابة الموردين - Vendors ] ---

@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if session.get('role') in ['vendor', 'staff']:
        return redirect(url_for('vendor_dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        success, msg, role = login_vendor(u, p) 
        if success:
            session.clear()
            session.permanent = True
            session['username'] = u
            session['role'] = role
            flash(msg, "success")
            return redirect(url_for('vendor_dashboard'))
        flash(msg, "danger")
    return render_template('login_vendor.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    role = session.get('role')
    username = session.get('username')
    
    if role not in ['vendor', 'staff']:
        return redirect(url_for('vendor_login'))
    
    vendor_data = models.Vendor.query.filter_by(username=username).first()
    if not vendor_data:
        session.clear()
        return redirect(url_for('vendor_login'))

    wallet = vendor_data.wallet
    recent_transactions = []
    if wallet:
        recent_transactions = models.Transaction.query.filter_by(wallet_id=wallet.id)\
                             .order_by(models.Transaction.created_at.desc()).limit(5).all()

    return render_template('vendor_dashboard.html', 
                           username=username,
                           vendor=vendor_data,
                           wallet=wallet,
                           transactions=recent_transactions)

# --- [ تسجيل الخروج ] ---

@app.route('/logout')
def logout():
    role = session.get('role')
    session.clear()
    flash("تم تسجيل الخروج بنجاح من برج المراقبة.", "info")
    if role == 'super_admin':
        return redirect(url_for('admin_login'))
    return redirect(url_for('vendor_login'))

# تشغيل السيرفر
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
