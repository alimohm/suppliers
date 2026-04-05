import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استيراد طبقات المنطق الموزع
import admin_logic
import vendor_logic

app = Flask(__name__)
app.config.from_object(Config)

# 1. تهيئة قاعدة البيانات وربطها بالتطبيق (Postgres)
init_db(app)

# 2. بناء الجداول وزرع بيانات الإدارة العليا (علي محجوب) عند الإقلاع
with app.app_context():
    db.create_all()
    models.seed_initial_data()

# --- [ بوابة التوجيه الذكية ] ---
@app.route('/')
def index():
    if session.get('role') == 'super_admin':
        return redirect(url_for('admin_dashboard'))
    elif session.get('role') in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('admin_login'))

# ==========================================
# 🛡️ قسم الإدارة العليا (برج المراقبة السيادي)
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        ok, msg = admin_logic.verify_admin_credentials(u, p)
        if ok:
            session.clear() # تأمين الجلسة
            session['username'] = u
            session['role'] = 'super_admin'
            return redirect(url_for('admin_dashboard'))
        flash(msg, "danger")
    return render_template('login_admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """ لوحة الإحصائيات العامة (Index) """
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    # جلب الإحصائيات الحقيقية من admin_logic
    vendors_count = models.Vendor.query.count()
    pending_count = models.Vendor.query.filter_by(status='قيد الانتظار').count()
    
    # حساب سيولة MAH الإجمالية في النظام
    total_balance = db.session.query(db.func.sum(models.Wallet.balance)).scalar() or 0.0
    
    # جلب آخر 5 عمليات مسجلة في النظام للجدول المختصر
    recent_tx = models.Transaction.query.order_by(models.Transaction.created_at.desc()).limit(5).all()

    return render_template('admin_dashboard.html', 
                           vendors_count=vendors_count, 
                           pending_count=pending_count, 
                           total_balance=total_balance,
                           recent_transactions=recent_tx)

@app.route('/admin/vendors-accreditation')
def vendors_accreditation():
    """ إدارة واعتماد الموردين (الجداول والنوافذ) """
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    # جلب قائمة الموردين كاملة
    all_vendors = models.Vendor.query.order_by(models.Vendor.created_at.desc()).all()
    
    return render_template('admin_accounts.html', vendors=all_vendors)

@app.route('/admin/approve/<int:vendor_id>', methods=['POST'])
def approve_vendor(vendor_id):
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    action = request.form.get('action') 
    success, msg = admin_logic.approve_vendor_logic(vendor_id, action)
    flash(msg, "success" if success else "danger")
    return redirect(url_for('vendors_accreditation'))

@app.route('/admin/add-vendor/post', methods=['POST'])
def admin_add_vendor_post():
    """ إضافة مورد جديد يدوياً من الإدارة وتدشين محفظة MAH """
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    try:
        # إنشاء كائن المورد
        new_v = models.Vendor(
            brand_name=request.form.get('brand_name'),
            username=request.form.get('username'),
            password=request.form.get('password'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            official_id=request.form.get('official_id'),
            status='نشط', # يتم التنشيط الفوري عند الإضافة اليدوية
            is_active=True
        )
        db.session.add(new_v)
        db.session.flush() # الحصول على ID المورد قبل الـ commit
        
        # تدشين المحفظة السيادية MAH
        wallet_no = f"MAH-{random.randint(100000, 999999)}"
        new_w = models.Wallet(wallet_number=wallet_no, vendor_id=new_v.id, balance=0.0)
        db.session.add(new_w)
        db.session.flush()
        
        # تسجيل عملية التدشين في كشف الحساب
        admin_logic.log_system_tx(new_w.id, 0.0, f"تم تدشين الكيان {new_v.brand_name} بنجاح")
        
        db.session.commit()
        flash(f"تم تسجيل {new_v.brand_name} بنجاح. رقم المحفظة: {wallet_no}", "success")
    
    except Exception as e:
        db.session.rollback()
        flash(f"فشل التسجيل: {str(e)}", "danger")
        
    return redirect(url_for('vendors_accreditation'))

# ==========================================
# 🏪 بوابة الموردين (الشركاء التجاريين)
# ==========================================

@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        ok, user_obj, role = vendor_logic.login_vendor(u, p)
        if ok:
            session.clear()
            session['vendor_id'] = user_obj.id
            session['username'] = u
            session['role'] = role
            return redirect(url_for('vendor_dashboard'))
        
        flash(user_obj if isinstance(user_obj, str) else "خطأ في بيانات الدخول", "danger")
    return render_template('login_vendor.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if session.get('role') not in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_login'))
    
    v_id = session.get('vendor_id')
    wallet = vendor_logic.get_wallet_details(v_id)
    products = vendor_logic.get_my_products(v_id)
    statement = vendor_logic.get_vendor_statement(v_id) 
    
    return render_template('vendor_dashboard.html', 
                           wallet=wallet, 
                           products=products, 
                           statement=statement)

@app.route('/vendor/add-product', methods=['POST'])
def vendor_add_product():
    if session.get('role') not in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_login'))
    
    success, msg = vendor_logic.add_new_product(session.get('vendor_id'), request.form)
    flash(msg, "success" if success else "warning")
    return redirect(url_for('vendor_dashboard'))

# --- [ نظام الخروج الآمن ] ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # التشغيل على بورت 8080 ليتوافق مع Cloud Run أو البيئات السحابية
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
