import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin
from logic import login_vendor, is_logged_in
from admin_logic import verify_admin_credentials, is_admin_logged_in

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات
init_db(app)

with app.app_context():
    db.create_all() # إنشاء وتحديث الجداول فوراً
    seed_admin()    # حقن بياناتك السيادية

# --- المسارات ---
@app.route('/')
def index():
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    if request.method == 'POST':
        u, p = request.form.get('username'), request.form.get('password')
        success, msg = login_vendor(u, p)
        if success: return redirect(url_for('dashboard'))
        flash(msg, "danger")
    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        u, p = request.form.get('admin_user'), request.form.get('admin_pass')
        success, msg = verify_admin_credentials(u, p)
        if success: return redirect(url_for('admin_dashboard'))
        flash(msg, "danger")
    return render_template('admin_login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    vendor = Vendor.query.get(session.get('user_id'))
    return render_template('dashboard.html', vendor=vendor)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in(): return redirect(url_for('admin_login_route'))
    return render_template('admin_dashboard.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080)) # توافق Railway
    app.run(host='0.0.0.0', port=port)
