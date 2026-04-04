import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استدعاء المنطق من الملفات الموجودة في Git لديك
# تأكد أن هذه الدوال تبحث في الجداول الصحيحة (AdminUser, Vendor, VendorStaff)
from vendor_logic import login_vendor 
from admin_logic import verify_admin_credentials

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

# --- [ منطقة السيادة: إعادة بناء القاعدة وحقن البيانات ] ---
with app.app_context():
    try:
        # ملاحظة: drop_all ستمسح البيانات القديمة، استخدمها فقط عند تحديث الهيكل (Models)
        # db.drop_all() 
        db.create_all() 
        models.seed_system() # سيحقن (علي، علي محمد، الموظف التجريبي) بكلمة مرور 123
        print("✅ تم تطهير القاعدة وحقن بيانات النظام بنجاح.")
    except Exception as e:
        print(f"❌ خطأ في القاعدة: {e}")

# --- [ بوابة الموردين والموظفين ] ---
@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        # دالة login_vendor يجب أن تبحث في جدولي Vendor و VendorStaff
        success, msg, role = login_vendor(u, p) 
        
        if success:
            session['username'] = u
            session['role'] = role # 'vendor_owner' أو 'vendor_staff'
            flash(msg, "success")
            return redirect(url_for('vendor_dashboard'))
        
        flash(msg, "danger")
    return render_template('login_vendor.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    # التحقق من الصلاحية: يجب أن يكون المورد أو موظفه مسجل دخول
    allowed_roles = ['vendor_owner', 'vendor_staff']
    if 'role' not in session or session.get('role') not in allowed_roles:
        return redirect(url_for('vendor_login'))
    
    # ميزة الإدارة: المالك فقط يرى المحفظة، الموظف لا يراها
    show_wallet = (session.get('role') == 'vendor_owner')
    
    return render_template('vendor_dashboard.html', 
                           username=session.get('username'), 
                           show_wallet=show_wallet)

# --- [ بوابة الإدارة العليا ] ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        # استخدام دالة التحقق من جدول AdminUser
        success, msg = verify_admin_credentials(u, p)
        if success:
            session['username'] = u
            session['role'] = 'super_admin' # تثبيت رتبة المدير
            flash(msg, "success")
            return redirect(url_for('admin_dashboard'))
        
        flash(msg, "danger")
    return render_template('login_admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    # حماية لوحة الإدارة: علي فقط من يدخل هنا
    if session.get('role') != 'super_admin':
        flash("عذراً، هذه المنطقة للإدارة العليا فقط.", "warning")
        return redirect(url_for('admin_login'))
        
    return render_template('admin_dashboard.html', username=session.get('username'))

# --- [ التوجيهات العامة ] ---
@app.route('/')
def index():
    # توجيه الزائر تلقائياً لبوابة الموردين كبداية
    return redirect(url_for('vendor_login'))

@app.route('/logout')
def logout():
    session.clear()
    flash("تم تسجيل الخروج بنجاح.", "info")
    return redirect(url_for('vendor_login'))

if __name__ == '__main__':
    # استخدام 8080 لتجنب التعارض مع المنافذ المحجوزة
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
