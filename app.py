import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- 1. تعريف التطبيق والتهيئة السيادية ---
app = Flask(__name__) #
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin #

# --- 2. استيراد المنطق بناءً على قاعدتك الذهبية ---
# المورد (بدون admin) من ملف logic.py
from logic import login_vendor, is_logged_in #
# الإدارة (مع admin) من ملف admin_logic.py
from admin_logic import verify_admin_credentials, is_admin_logged_in #

app.config.from_object(Config)
init_db(app)

with app.app_context():
    db.create_all() # تحديث الجداول فوراً لحل نقص الأعمدة
    seed_admin() # حقن بياناتك (علي محجوب)

# --- 3. بوابة دخول المورد (Vendor Login) ---
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        # استدعاء دالة المورد من logic.py
        success, message = login_vendor(u, p)
        if success:
            flash(message, "success")
            return redirect(url_for('dashboard'))
        flash(message, "danger")
            
    return render_template('login.html') #

# --- 4. بوابة دخول الإدارة (Admin Login) ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        
        # استدعاء دالة الإدارة من admin_logic.py
        success, message = verify_admin_credentials(u, p)
        if success:
            flash(message, "success")
            return redirect(url_for('admin_dashboard'))
        flash(message, "danger")
            
    return render_template('admin_login.html') #

# --- 5. لوحات التحكم ---
@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    vendor = Vendor.query.get(session.get('user_id'))
    return render_template('dashboard.html', vendor=vendor)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in(): return redirect(url_for('admin_login_route'))
    all_vendors = Vendor.query.all()
    return render_template('admin_dashboard.html', vendors=all_vendors)

# تسجيل الخروج الآمن
@app.route('/logout')
def logout():
    session.clear()
    flash("تم تأمين النظام والخروج.", "info")
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080)) # التوافق معRailway
    app.run(host='0.0.0.0', port=port)
