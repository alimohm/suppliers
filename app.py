import os
import random
from datetime import datetime
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

# 2. بناء الجداول وتأمين البيانات الأولية عند التشغيل
with app.app_context():
    db.create_all()
    models.seed_initial_data()

# --- [ بوابة التوجيه الرئيسية ] ---
@app.route('/')
def index():
    if session.get('role') == 'super_admin':
        return redirect(url_for('admin_dashboard'))
    elif session.get('role') == 'vendor':
        return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('admin_login'))

# --- [ قسم الإدارة العليا - برج المراقبة ] ---

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
    return render_template('admin_main.html', username=session.get('username'), stats=stats)

@app.route('/admin/vendors-accreditation')
def vendors_accreditation():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    vendors = get_dashboard_data()
    pending = get_admin_stats().get('pending', 0)
    return render_template('admin_accounts.html', vendors=vendors, pending_count=pending)

@app.route('/admin/add-vendor')
def admin_add_vendor():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    return render_template('admin_add_vendor.html')

@app.route('/admin/add-vendor/post', methods=['POST'])
def admin_add_vendor_post():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    # استخراج كافة البيانات الرسمية
    brand = request.form.get('brand_name')
    user = request.form.get('username')
    pw = request.form.get('password')
    phone = request.form.get('phone')
    address = request.form.get('address')
    official_id = request.form.get('official_id')
    
    # 1. إنشاء المورد وتفعيله كـ "نشط" فوراً
    new_v = models.Vendor(
        brand_name=brand, 
        username=user, 
        password=pw, 
        phone=phone,
        address=address,
        official_id=official_id,
        status='نشط', 
        is_active=True
    )
    db.session.add(new_v)
    db.session.flush() # للحصول على ID المورد قبل الحفظ النهائي
    
    # 2. إنشاء المحفظة السيادية MAH
    wallet_no = f"MAH-{random.randint(100000, 999999)}"
    new_wallet = models.Wallet(wallet_number=wallet_no, vendor_id=new_v.id, balance=0.0)
    db.session.add(new_wallet)
    db.session.flush()

    # 3. تسجيل أول عملية في كشف الحساب (افتتاح المحفظة)
    first_tx = models.Transaction(
        wallet_id=new_wallet.id,
        tx_type='إيداع',
        amount=0.0,
        prev_balance=0.0,
        new_balance=0.0,
        details="افتتاح المحفظة السيادية واعتماد المورد"
    )
    db.session.add(first_tx)
    
    db.session.commit()
    flash(f"تم اعتماد {brand} بنجاح ومنحه المحفظة {wallet_no}", "success")
    return redirect(url_for('vendors_accreditation'))

@app.route('/admin/approve/<int:vendor_id>', methods=['POST'])
def approve_vendor(vendor_id):
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    action = request.form.get('action') # 'approve' أو 'reject'
    vendor = models.Vendor.query.get(vendor_id)
    
    if not vendor:
        flash("المورد غير موجود", "danger")
        return redirect(url_for('vendors_accreditation'))

    if action == 'approve':
        vendor.status = 'نشط'
        vendor.is_active = True
        # إنشاء المحفظة وتدشين كشف الحساب
        wallet_no = f"MAH-{random.randint(100000, 999999)}"
        new_w = models.Wallet(wallet_number=wallet_no, vendor_id=vendor.id)
        db.session.add(new_w)
        db.session.commit()
        flash(f"تم قبول المورد وتفعيل المحفظة {wallet_no}", "success")
    
    elif action == 'reject':
        vendor.status = 'مرفوض'
        vendor.is_active = False
        db.session.commit()
        flash("تم رفض طلب المورد وتغيير حالته إلى مرفوض", "warning")
        
    return redirect(url_for('vendors_accreditation'))

# --- [ بوابة الموردين ] ---

@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        vendor = models.Vendor.query.filter_by(username=u, password=p).first()
        
        if vendor:
            if vendor.is_active and vendor.status == 'نشط':
                session['vendor_id'] = vendor.id
                session['username'] = vendor.username
                session['role'] = 'vendor'
                return redirect(url_for('vendor_dashboard'))
            else:
                flash(f"لا يمكن الدخول. حالة الحساب: {vendor.status}", "danger")
        else:
            flash("بيانات الدخول غير صحيحة", "danger")
    return render_template('login_vendor.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if session.get('role') != 'vendor':
        return redirect(url_for('vendor_login'))
    vendor = models.Vendor.query.get(session.get('vendor_id'))
    # جلب كشف الحساب لعرضه في اللوحة
    transactions = models.Transaction.query.filter_by(wallet_id=vendor.wallet.id).order_by(models.Transaction.created_at.desc()).all()
    return render_template('vendor_dashboard.html', vendor=vendor, transactions=transactions)

# --- [ نظام الخروج ] ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
