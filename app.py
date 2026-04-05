import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استيراد طبقات المنطق الموزع (Business Logic)
import admin_logic
import vendor_logic

app = Flask(__name__)
app.config.from_object(Config)

# 1. تهيئة قاعدة البيانات (PostgreSQL)
init_db(app)

# 2. بناء الجداول وزرع البيانات الأولية عند الإقلاع
with app.app_context():
    db.create_all()
    # تأكد أن هذه الدالة في models.py تنشئ حساب "علي محجوب" الافتراضي
    models.seed_initial_data()

# --- [ نظام التوجيه الذكي (Routing Gateway) ] ---
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
    """ 
    لوحة الإحصائيات (Index): مرتبطة بربط مباشر مع قاعدة البيانات 
    لإظهار الأرقام الحقيقية في الكروت والعدادات.
    """
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    # ربط منطقي: جلب الأرقام الحية
    vendors_count = models.Vendor.query.count()
    pending_count = models.Vendor.query.filter_by(status='قيد الانتظار').count()
    
    # حساب إجمالي سيولة MAH في النظام
    total_mah = db.session.query(db.func.sum(models.Wallet.balance)).scalar() or 0.0
    
    # جلب آخر 5 عمليات مالية لجدول الرقابة
    recent_tx = models.Transaction.query.order_by(models.Transaction.created_at.desc()).limit(5).all()

    return render_template('admin_dashboard.html', 
                           vendors_count=vendors_count, 
                           pending_count=pending_count, 
                           total_mah=total_mah,
                           recent_transactions=recent_tx)

@app.route('/admin/vendors-accreditation')
def vendors_accreditation():
    """ صفحة إدارة الموردين: تدعم عرض الأيقونات والتنسيق المتجاوب """
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    # جلب كافة الموردين مرتبين حسب الأحدث
    all_vendors = models.Vendor.query.order_by(models.Vendor.created_at.desc()).all()
    return render_template('admin_accounts.html', vendors=all_vendors)

@app.route('/admin/approve/<int:vendor_id>', methods=['POST'])
def approve_vendor(vendor_id):
    """ مسار اتخاذ القرار (تفعيل أو حظر) """
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    action = request.form.get('action') 
    success, msg = admin_logic.approve_vendor_logic(vendor_id, action)
    flash(msg, "success" if success else "danger")
    return redirect(url_for('vendors_accreditation'))

@app.route('/admin/add-vendor/post', methods=['POST'])
def admin_add_vendor_post():
    """ 
    إضافة مورد يدوياً: يربط المورد بمحفظة MAH فوراً 
    ويخزن البيانات في قاعدة البيانات بشكل دائم.
    """
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    try:
        # إنشاء المورد
        new_v = models.Vendor(
            brand_name=request.form.get('brand_name'),
            username=request.form.get('username'),
            password=request.form.get('password'), # يفضل تشفيرها بـ werkzeug.security
            phone=request.form.get('phone'),
            status='نشط',
            is_active=True
        )
        db.session.add(new_v)
        db.session.flush() # الحصول على ID قبل الحفظ النهائي
        
        # إنشاء المحفظة المالية المرتبطة (Infrastructure Link)
        wallet_no = f"MAH-{random.randint(100000, 999999)}"
        new_w = models.Wallet(wallet_number=wallet_no, vendor_id=new_v.id, balance=0.0)
        db.session.add(new_w)
        
        # تسجيل عملية التدشين في سجلات النظام
        log = models.Transaction(wallet_id=new_w.id, amount=0.0, tx_type='system', description="تدشين محفظة سيادية")
        db.session.add(log)
        
        db.session.commit()
        flash(f"تم إنشاء الكيان {new_v.brand_name} بنجاح محفظة رقم: {wallet_no}", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"خطأ في البنية التحتية: {str(e)}", "danger")
        
    return redirect(url_for('vendors_accreditation'))

# ==========================================
# 🏪 بوابة الموردين (الشركاء)
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
        flash("خطأ في بيانات الدخول", "danger")
    return render_template('login_vendor.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    """ لوحة المورد: مرتبطة بمحفظته ومنتجاته فقط """
    if session.get('role') not in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_login'))
    
    v_id = session.get('vendor_id')
    wallet = models.Wallet.query.filter_by(vendor_id=v_id).first()
    products = models.Product.query.filter_by(vendor_id=v_id).all()
    
    return render_template('vendor_dashboard.html', wallet=wallet, products=products)

# --- [ نظام الخروج والإنهاء ] ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # بورت 8080 للبيئات السحابية
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
