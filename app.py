import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استدعاء المنطق البرمجي
from vendor_logic import login_vendor 
from admin_logic import verify_admin_credentials

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات
init_db(app)

# --- [ منطقة السيادة: بناء القاعدة وحقن البيانات ] ---
with app.app_context():
    try:
        db.create_all() 
        models.seed_system()
        print("✅ تم فحص القاعدة وتوليد المحافظ السيادية بنجاح.")
    except Exception as e:
        print(f"❌ خطأ في القاعدة: {e}")

# --- [ التوجيهات العامة ] ---
@app.route('/')
def index():
    if 'role' in session:
        if session['role'] == 'super_admin':
            return redirect(url_for('admin_dashboard'))
        elif session['role'] in ['vendor_owner', 'vendor_staff']:
            return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('vendor_login'))

# --- [ بوابة الإدارة: برج المراقبة ] ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('role') == 'super_admin':
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        success, msg = verify_admin_credentials(u, p)
        if success:
            session.clear()
            session.permanent = True
            session['username'] = u
            session['role'] = 'super_admin'
            flash("تم الدخول لبرج المراقبة بنجاح 🛡️", "success")
            return redirect(url_for('admin_dashboard'))
        flash(msg, "danger")
    return render_template('login_admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'super_admin':
        flash("🚫 صلاحيات غير كافية للوصول لبرج المراقبة", "danger")
        return redirect(url_for('admin_login'))
    
    all_vendors = models.Vendor.query.all()
    return render_template('admin_dashboard.html', 
                           username=session.get('username'), 
                           vendors=all_vendors)

@app.route('/admin/create-vendor', methods=['POST'])
def create_vendor():
    if session.get('role') != 'super_admin': return redirect(url_for('admin_login'))
    
    u = request.form.get('username', '').strip()
    b = request.form.get('brand_name', '').strip()
    p = request.form.get('password', '').strip()

    if models.Vendor.query.filter_by(username=u).first():
        flash("⚠️ اسم المستخدم موجود مسبقاً.", "warning")
    else:
        try:
            new_v = models.Vendor(username=u, brand_name=b, password=p)
            db.session.add(new_v)
            db.session.flush() 

            wallet_num = f"MAH-{random.randint(100,999)}-{random.randint(1000,9999)}"
            new_wallet = models.Wallet(wallet_number=wallet_num, balance=0.0, vendor_id=new_v.id)
            db.session.add(new_wallet)
            
            db.session.commit()
            flash(f"✅ تم اعتماد المورد '{b}' بنجاح.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ فشل الاعتماد: {str(e)}", "danger")
            
    return redirect(url_for('admin_dashboard'))

# --- [ بوابة الموردين: سوقك الذكي ] ---

@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if 'role' in session and session.get('role') in ['vendor_owner', 'vendor_staff']:
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
    if 'role' not in session or session.get('role') not in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_login'))
    
    username = session.get('username')
    role = session.get('role')

    # جلب البيانات بناءً على نوع المستخدم (مالك أم موظف)
    if role == 'vendor_owner':
        vendor_data = models.Vendor.query.filter_by(username=username).first()
    else:
        staff = models.VendorStaff.query.filter_by(username=username).first()
        vendor_data = staff.vendor if staff else None
    
    if not vendor_data:
        session.clear()
        flash("خطأ في استعادة بيانات السيادة، يرجى إعادة الدخول.", "danger")
        return redirect(url_for('vendor_login'))

    # جلب المحفظة بأمان لتجنب AttributeError
    wallet = vendor_data.wallet
    wallet_no = wallet.wallet_number if wallet else "N/A"
    balance = wallet.balance if wallet else 0.0
    
    return render_template('vendor_dashboard.html', 
                           username=username,
                           vendor=vendor_data,
                           wallet_no=wallet_no, 
                           balance=balance)

@app.route('/vendor/add-product')
def add_product():
    if 'role' not in session or session.get('role') not in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_login'))
    return render_template('vendor_add_product.html')

# --- [ نظام الخروج ] ---

@app.route('/logout')
def logout():
    role = session.get('role')
    session.clear()
    flash("تم تسجيل الخروج بنجاح.", "info")
    if role == 'super_admin':
        return redirect(url_for('admin_login'))
    return redirect(url_for('vendor_login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    # إيقاف debug في الإنتاج لزيادة الأمان
    app.run(host='0.0.0.0', port=port, debug=False)
