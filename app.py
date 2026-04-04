import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استدعاء المنطق من الملفات الموجودة في Git لديك
from vendor_logic import login_vendor
from admin_logic import verify_admin_credentials

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

# --- [ منطقة السيادة: إعادة بناء القاعدة وحقن البيانات ] ---
with app.app_context():
    try:
        # اترك السطرين القادمين مفعلين لمرة واحدة عند الرفع لتصحيح Postgres
        db.drop_all() 
        db.create_all() 
        models.seed_system() # هذا سيحقن "علي محجوب" بكلمة مرور نصية
        print("✅ تم تطهير القاعدة وحقن بيانات 'علي محجوب' بنجاح.")
    except Exception as e:
        print(f"❌ خطأ في القاعدة: {e}")

# --- [ بوابة الموردين ] ---
@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        success, msg = login_vendor(u, p)
        if success:
            flash(msg, "success")
            return redirect(url_for('vendor_dashboard'))
        
        flash(msg, "danger")
    # التأكد من الاسم الجديد للملف
    return render_template('login_vendor.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if 'role' not in session or 'vendor' not in str(session.get('role')):
        return redirect(url_for('vendor_login'))
    
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
        
        # استخدام دالة التحقق المعدلة
        success, msg = verify_admin_credentials(u, p)
        if success:
            flash(msg, "success")
            return redirect(url_for('admin_dashboard'))
        
        flash(msg, "danger")
    # التأكد من الاسم الجديد للملف
    return render_template('login_admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html', username=session.get('username'))

@app.route('/')
def index():
    return redirect(url_for('vendor_login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('vendor_login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
