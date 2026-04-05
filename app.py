import os
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
    return redirect(url_for('admin_login'))

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
    # تم الربط مع login_admin.html كما في ملفاتك
    return render_template('login_admin.html')

# --- [ لوحة تحكم الإدارة العليا ] ---

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    stats = get_admin_stats()
    # تم الربط مع admin_main.html كما في هيكل القوالب الخاص بك
    return render_template('admin_main.html', 
                           username=session.get('username'), 
                           stats=stats)

# --- [ إدارة واعتماد الحسابات ] ---

@app.route('/admin/vendors-accreditation')
def vendors_accreditation():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    vendors = get_dashboard_data()
    pending = get_admin_stats().get('pending', 0)
    # تم الربط مع admin_accounts.html
    return render_template('admin_accounts.html', 
                           vendors=vendors, 
                           pending_count=pending,
                           username=session.get('username'))

@app.route('/admin/approve/<int:vendor_id>', methods=['POST'])
def approve_vendor(vendor_id):
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    success, msg = approve_vendor_logic(vendor_id)
    flash(msg, "success" if success else "danger")
    return redirect(url_for('vendors_accreditation'))

# --- [ بوابة الموردين ] ---

@app.route('/vendor/login')
def vendor_login():
    return render_template('login_vendor.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    # سيتم ربط المنطق لاحقاً
    return render_template('vendor_dashboard.html')


# 1. مسار عرض صفحة إضافة مورد يدوي
@app.route('/admin/add-vendor')
def admin_add_vendor():
    return render_template('admin_add_vendor.html')

# 2. معالجة الإضافة اليدوية (تفعيل فوري)
@app.route('/admin/add-vendor/post', methods=['POST'])
def admin_add_vendor_post():
    brand = request.form.get('brand_name')
    user = request.form.get('username')
    pw = request.form.get('password')
    
    # إضافة المورد وتفعيله فوراً
    new_v = models.Vendor(brand_name=brand, username=user, password=pw, is_active=True)
    db.session.add(new_v)
    db.session.commit()
    
    # إنشاء المحفظة MAH تلقائياً
    import random
    wallet_no = f"MAH-{random.randint(1000, 9999)}"
    db.session.add(models.Wallet(wallet_number=wallet_no, vendor_id=new_v.id))
    db.session.commit()
    
    flash(f"تم إضافة {brand} وتفعيل هويته المالية.", "success")
    return redirect(url_for('vendors_accreditation'))
    

# --- [ نظام تسجيل الخروج ] ---

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    # ضمان العمل على منصة Railway باستخدام المنفذ الديناميكي
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)



# --- [ بوابة الموردين - الدخول واللوحة ] ---

@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        # البحث عن المورد في قاعدة البيانات وتأكد من أنه معتمد
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
    # منع الدخول إلا للموردين المسجلين
    if session.get('role') != 'vendor':
        return redirect(url_for('vendor_login'))
    
    vendor = models.Vendor.query.get(session.get('vendor_id'))
    return render_template('vendor_dashboard.html', vendor=vendor)
