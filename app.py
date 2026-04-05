import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استيراد طبقات المنطق الموزع (Business Logic)
import admin_logic
import vendor_logic
import finance_logic

app = Flask(__name__)
app.config.from_object(Config)

# 1. تهيئة قاعدة البيانات (PostgreSQL/SQLite)
init_db(app)

# 2. بناء الجداول وزرع البيانات الأولية (علي محجوب) عند الإقلاع
with app.app_context():
    db.create_all()
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
# 🛡️ قسم الإدارة العليا (برج المراقبة - علي محجوب)
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
    """ لوحة الإحصائيات المركزية الحية """
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    vendors_count = models.Vendor.query.count()
    pending_count = models.Vendor.query.filter_by(status='قيد الانتظار').count()
    total_mah = db.session.query(db.func.sum(models.Wallet.balance)).scalar() or 0.0
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
    
    all_vendors = models.Vendor.query.order_by(models.Vendor.created_at.desc()).all()
    return render_template('admin_accounts.html', vendors=all_vendors)

@app.route('/admin/add-vendor/post', methods=['POST'])
def admin_add_vendor_post():
    """ الحفظ التلقائي للمورد مع توليد محفظة MAH فوراً """
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    try:
        new_v = models.Vendor(
            brand_name=request.form.get('brand_name'),
            username=request.form.get('username'),
            password=request.form.get('password'), 
            phone=request.form.get('phone'),
            status='نشط',
            is_active=True
        )
        db.session.add(new_v)
        db.session.flush() 
        
        wallet_no = f"MAH-{random.randint(100000, 999999)}"
        new_w = models.Wallet(wallet_number=wallet_no, vendor_id=new_v.id, balance=0.0)
        db.session.add(new_w)
        
        log = models.Transaction(wallet_id=new_w.id, amount=0.0, tx_type='تأسيس', description=f"تدشين الكيان: {new_v.brand_name}")
        db.session.add(log)
        
        db.session.commit()
        flash(f"تم بنجاح ربط {new_v.brand_name} بمحفظة رقم {wallet_no}", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"فشل الربط التلقائي: {str(e)}", "danger")
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
        flash("بيانات الدخول غير صحيحة", "danger")
    return render_template('login_vendor.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if session.get('role') not in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_login'))
    
    v_id = session.get('vendor_id')
    wallet = models.Wallet.query.filter_by(vendor_id=v_id).first()
    products = models.Product.query.filter_by(vendor_id=v_id).all()
    
    return render_template('vendor_dashboard.html', wallet=wallet, products=products)

# ==========================================
# 💸 النظام المالي (محرك التحويلات)
# ==========================================

@app.route('/vendor/transfer', methods=['POST'])
def vendor_transfer_post():
    """ مسار تنفيذ التحويل المالي السيادي """
    if session.get('role') not in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_login'))

    v_id = session.get('vendor_id')
    sender_wallet = models.Wallet.query.filter_by(vendor_id=v_id).first()
    
    target_wallet_no = request.form.get('target_wallet')
    amount_str = request.form.get('amount', '0')
    amount = float(amount_str) if amount_str else 0.0
    note = request.form.get('note', 'تحويل صادر')

    success, message = finance_logic.transfer_mah(sender_wallet.id, target_wallet_no, amount, note)
    flash(message, "success" if success else "danger")
    return redirect(url_for('vendor_dashboard'))

# --- [ نظام الخروج والإنهاء ] ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
