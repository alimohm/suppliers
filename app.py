import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models
from vendor_logic import login_vendor

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

# --- [ منطقة السيادة وإعادة الهيكلة ] ---
with app.app_context():
    try:
        # تحذير: السطر التالي سيمسح البيانات القديمة لتصحيح هيكل الجداول
        # قم بتعطيله بوضع (#) بعد أول عملية تشغيل ناجحة
        db.drop_all() 
        db.create_all() 
        models.seed_system()
        print("✅ تم تطهير قاعدة البيانات وحقن بيانات 'علي محجوب' بنجاح.")
    except Exception as e:
        print(f"❌ خطأ في تهيئة القاعدة: {e}")

# --- [ المسارات العامة ] ---
@app.route('/')
def index():
    return redirect(url_for('vendor_login'))

# --- [ مسارات الموردين (Vendors) ] ---
@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        success, msg = login_vendor(u, p)
        if success:
            return redirect(url_for('vendor_dashboard'))
        flash(msg, "danger")
    return render_template('vendor_login.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if 'role' not in session or 'vendor' not in session.get('role'):
        return redirect(url_for('vendor_login'))
    show_wallet = (session.get('role') == 'vendor_owner')
    return render_template('vendor_dashboard.html', 
                           username=session.get('username'), 
                           show_wallet=show_wallet)

# --- [ مسارات الإدارة العليا (علي محجوب) ] ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        if u == "علي محجوب" and p == "admin_password_123":
            session['role'] = 'super_admin'
            session['username'] = u
            return redirect(url_for('admin_dashboard'))
        flash("بيانات دخول الإدارة غير صحيحة", "danger")
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html', username=session.get('username'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('vendor_login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
