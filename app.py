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

# 1. تهيئة قاعدة البيانات
init_db(app)

# 2. بناء الجداول وزرع البيانات الأولية (علي محجوب)
with app.app_context():
    db.create_all()
    models.seed_initial_data()

# --- [ نظام التوجيه الذكي ] ---
@app.route('/')
def index():
    if session.get('role') == 'super_admin':
        return redirect(url_for('admin_dashboard'))
    elif session.get('role') in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('admin_login'))

# ==========================================
# 🛡️ قسم الإدارة العليا (برج المراقبة)
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        ok, msg = admin_logic.verify_admin_credentials(u, p)
        if ok:
            session.clear()
            session['username'] = u
            session['role'] = 'super_admin'
            return redirect(url_for('admin_dashboard'))
        flash(msg, "danger")
    return render_template('login_admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """ لوحة الإحصائيات المركزية مرتبطة بالقاعدة حياً """
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    # جلب الأرقام الحية للعدادات
    vendors_count = models.Vendor.query.count()
    pending_count = models.Vendor.query.filter_by(status='قيد الانتظار').count()
    total_mah = db.session.query(db.func.sum(models.Wallet.balance)).scalar() or 0.0
    
    # جلب آخر 5 عمليات وتعديل الترتيب ليكون حسب التاريخ التلقائي
    recent_tx = models.Transaction.query.order_by(models.Transaction.created_at.desc()).limit(5).all()

    return render_template('admin_dashboard.html', 
                           vendors_count=vendors_count, 
                           pending_count=pending_count, 
                           total_mah=total_mah,
                           recent_transactions=recent_tx)

@app.route('/admin/vendors-accreditation')
def vendors_accreditation():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    # عرض الموردين مع ضمان ظهور تاريخ الانضمام التلقائي
    all_vendors = models.Vendor.query.order_by(models.Vendor.created_at.desc()).all()
    return render_template('admin_accounts.html', vendors=all_vendors)

@app.route('/admin/add-vendor/post', methods=['POST'])
def admin_add_vendor_post():
    """ الحفظ التلقائي والربط المنطقي بين المورد والمحفظة """
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    try:
        # 1. إنشاء المورد (تاريخ created_at سيعمل تلقائياً من models.py)
        new_v = models.Vendor(
            brand_name=request.form.get('brand_name'),
            username=request.form.get('username'),
            password=request.form.get('password'), 
            phone=request.form.get('phone'),
            status='نشط', # يتم التفعيل فوراً عند الإضافة من قبل علي محجوب
            is_active=True
        )
        db.session.add(new_v)
        db.session.flush() # تثبيت مؤقت لجلب ID المورد
        
        # 2. إنشاء المحفظة السيادية وربطها (Infrastructure Link)
        wallet_no = f"MAH-{random.randint(100000, 999999)}"
        new_w = models.Wallet(
            wallet_number=wallet_no, 
            vendor_id=new_v.id, 
            balance=0.0
        )
        db.session.add(new_w)
        
        # 3. توثيق العملية مالياً (Audit Trail)
        log = models.Transaction(
            wallet_id=new_w.id, 
            amount=0.0, 
            tx_type='تأسيس', 
            details=f"تدشين الكيان: {new_v.brand_name}"
        )
        db.session.add(log)
        
        db.session.commit() # الحفظ النهائي لجميع الجداول معاً
        flash(f"تم بنجاح ربط {new_v.brand_name} بمحفظة رقم {wallet_no}", "success")
        
    except Exception as e:
        db.session.rollback() # التراجع في حالة وجود خطأ لضمان سلامة القاعدة
        flash(f"فشل الربط التلقائي: {str(e)}", "danger")
        
    return redirect(url_for('vendors_accreditation'))

# ==========================================
# 🏪 بوابة الموردين (الشركاء)
# ==========================================

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if session.get('role') not in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_login'))
    
    v_id = session.get('vendor_id')
    # ربط منطقي لسحب بيانات المورد من محفظته الخاصة فقط
    wallet = models.Wallet.query.filter_by(vendor_id=v_id).first()
    products = models.Product.query.filter_by(vendor_id=v_id).all()
    
    return render_template('vendor_dashboard.html', wallet=wallet, products=products)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
