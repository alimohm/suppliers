import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استدعاء المنطق البرمجي (المعزز بالأداء العالي)
from vendor_logic import login_vendor 
from admin_logic import (
    verify_admin_credentials, 
    manage_accounts_logic, 
    create_vendor_logic, 
    get_admin_stats
)

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات - هنا تبدأ السيادة التقنية
init_db(app)

with app.app_context():
    try:
        db.create_all() 
        models.seed_system()
        print("✅ نظام محجوب أونلاين: السيادة التقنية جاهزة وقاعدة البيانات متصلة.")
    except Exception as e:
        print(f"❌ خطأ في تهيئة النظام: {e}")

# --- [ التوجيه الرئيسي ] ---

@app.route('/')
def index():
    role = session.get('role')
    if role == 'super_admin':
        return redirect(url_for('admin_dashboard'))
    elif role in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('vendor_login'))

# --- [ بوابة الإدارة - Super Admin ] ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('role') == 'super_admin':
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        # استعلام مؤندكس (Indexed Query) سريع جداً
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
    
    # جلب الإحصائيات باستخدام Count سريع بفضل الـ Index
    stats = get_admin_stats()
    return render_template('admin_main.html', 
                           username=session.get('username'), 
                           stats=stats)

@app.route('/admin/vendors-accreditation')
def vendors_accreditation():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    # جلب الموردين مرتبين حسب الـ ID المفهرس
    all_vendors = manage_accounts_logic() 
    return render_template('admin_accounts.html', 
                           username=session.get('username'), 
                           vendors=all_vendors)

@app.route('/admin/create-vendor', methods=['POST'])
def create_vendor_route():
    if session.get('role') != 'super_admin': 
        return redirect(url_for('admin_login'))
    
    success, msg = create_vendor_logic()
    flash(msg, "success" if success else "danger")
    return redirect(url_for('vendors_accreditation'))

# --- [ دوال الاعتماد السيادي - تمنع الانهيار ] ---

@app.route('/admin/activate-vendor/<int:vendor_id>', methods=['POST'])
def activate_vendor(vendor_id):
    """تفعيل الحساب ومنح رقم محفظة MAH بشكل فوري"""
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    # استخدام Get بـ Index (أسرع أنواع البحث)
    vendor = models.Vendor.query.get_or_404(vendor_id)
    vendor.is_active = True
    vendor.status = "نشط"
    
    if not vendor.wallet:
        new_wallet = models.Wallet(vendor_id=vendor.id)
        db.session.add(new_wallet)
    
    db.session.commit()
    flash(f"تم تفعيل سيادة المورد {vendor.brand_name} ومنحه محفظة MAH بنجاح ✨", "success")
    return redirect(url_for('vendors_accreditation'))

@app.route('/admin/vendor-profile/<int:vendor_id>')
def view_vendor_profile(vendor_id):
    """عرض تفاصيل المورد والوثائق (الهوية والسجل)"""
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    vendor = models.Vendor.query.get_or_404(vendor_id)
    return render_template('vendor_profile.html', vendor=vendor)

# --- [ بوابة الموردين - Vendors ] ---

@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if session.get('role') in ['vendor_owner', 'vendor_staff']:
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
    
    if role not in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_login'))
    
    # استعلام مستفيد من الـ Index لسرعة جلب بيانات المورد
    vendor_data = models.Vendor.query.filter_by(username=username).first() if role == 'vendor_owner' else None
    if not vendor_data and role == 'vendor_staff':
        staff = models.VendorStaff.query.filter_by(username=username).first()
        vendor_data = staff.vendor if staff else None

    if not vendor_data:
        session.clear()
        return redirect(url_for('vendor_login'))

    wallet = vendor_data.wallet
    return render_template('vendor_dashboard.html', 
                           username=username, 
                           vendor=vendor_data,
                           wallet_no=wallet.wallet_number if wallet else "N/A", 
                           balance=wallet.balance if wallet else 0.0)

# --- [ تسجيل الخروج ] ---

@app.route('/logout')
def logout():
    role = session.get('role')
    session.clear()
    flash("تم تسجيل الخروج من نظام محجوب أونلاين بنجاح.", "info")
    return redirect(url_for('admin_login' if role == 'super_admin' else 'vendor_login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
